from pymongo.errors import BulkWriteError

class ProtocoloRepository:
    def __init__(self, db):
        self.__db = db

    async def inserir_protocolo(self, protocolo: dict) -> bool:
        
        try:
            protocolo_no_db = await self.__db.protocolos.find_one(
                {"solicitacaoId": protocolo["solicitacaoId"], "evento": protocolo["evento"]}
            )

            if protocolo_no_db is None:
                await self.__db.protocolos.insert_one(protocolo)
                return True

            await self.__db.protocolos.delete_one(
                   {"solicitacaoId": protocolo["solicitacaoId"], "evento": protocolo["evento"]}
            )
            await self.__db.protocolos.insert_one(protocolo)
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir o protocolo: {e}")
            return False
        
    async def inserir_protocolos_em_lote(self, protocolos: list[dict]) -> bool:
        try:
            if not protocolos:
                return False

            filtros = [{"solicitacaoId": a["solicitacaoId"], "evento": a["evento"]} for a in protocolos]
            await self.__db.protocolos.delete_many({"$or": filtros})

            await self.__db.protocolos.insert_many(protocolos)
            return True
        except BulkWriteError as bwe:
            print(f"❌ Erro de escrita em lote: {bwe.details}")
            return False
        except Exception as e:
            print(f"❌ Erro ao inserir protocolos em lote: {e}")
            return False

    async def remover_protocolo(self, solicitacaoId: int) -> bool:
        try:
            await self.__db.protocolos.delete_many({"solicitacaoId": solicitacaoId})
            return True
        except Exception as e:
            print(f"❌ Erro ao remover o protocolo: {e}")
            return False

    async def atualizar_protocolo(
        self, solicitacaoId: int, per_apur: str, protocolo: str, codigo_retorno: str, descricao_retorno: str
    ) -> bool:
        """
        Atualiza os campos codigo_retorno e descricao_retorno
        dentro do array 'protocolo' filtrando pelo solicitacaoId, per_apur e protocolo.
        """
        try:
            resultado = await self.__db.protocolos.update_one(
                {
                    "solicitacaoId": solicitacaoId,
                    "protocolo.per_apur": per_apur,
                    "protocolo.protocolo": protocolo
                },
                {
                    "$set": {
                        "protocolo.$.codigo_retorno": codigo_retorno,
                        "protocolo.$.descricao_retorno": descricao_retorno
                    }
                }
            )

            if resultado.matched_count == 0:
                print("⚠️ Nenhum protocolo encontrado para atualizar.")
                return False

            return True
        except Exception as e:
            print(f"❌ Erro ao atualizar protocolo: {e}")
            return False

    async def buscar_por_solicitacao_id(self, solicitacaoId: int) -> list[dict]:
        try:
            return await self.__db.protocolos.find({"solicitacaoId": solicitacaoId}).to_list(length=None)
        except Exception as e:
            print(f"❌ Erro ao buscar protocolo por solicitacaoId: {e}")
            return []
    
    async def buscar_por_solicitacao_id_e_evento(self, solicitacaoId: int, evento: str) -> dict | None:
        try:
            return await self.__db.protocolos.find_one({"solicitacaoId": solicitacaoId, "evento": evento})
        except Exception as e:
            print(f"❌ Erro ao buscar protocolo por solicitacaoId e evento: {e}")
            return None