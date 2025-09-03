from pymongo.errors import BulkWriteError

class ArquivoRepository:
    def __init__(self, db):
        self.__db = db

    async def inserir_arquivo(self, arquivo: dict) -> bool:
        
        try:
            arquivo_no_db = await self.__db.arquivos.find_one(
                {"solicitacaoId": arquivo["solicitacaoId"], "cpf": arquivo["cpf"]}
            )

            if arquivo_no_db is None:
                await self.__db.arquivos.insert_one(arquivo)
                return True

            await self.__db.arquivos.delete_one(
                {"solicitacaoId": arquivo["solicitacaoId"], "cpf": arquivo["cpf"]}
            )
            await self.__db.arquivos.insert_one(arquivo)
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir o arquivo: {e}")
            return False
        
    async def inserir_arquivos_em_lote(self, arquivos: list[dict]) -> bool:
        try:
            if not arquivos:
                return False

            filtros = [{"solicitacaoId": a["solicitacaoId"], "cpf": a["cpf"]} for a in arquivos]
            await self.__db.arquivos.delete_many({"$or": filtros})

            await self.__db.arquivos.insert_many(arquivos)
            return True
        except BulkWriteError as bwe:
            print(f"❌ Erro de escrita em lote: {bwe.details}")
            return False
        except Exception as e:
            print(f"❌ Erro ao inserir arquivos em lote: {e}")
            return False

    async def remover_arquivo(self, solicitacaoId: int) -> bool:
        try:
            await self.__db.arquivos.delete_many({"solicitacaoId": solicitacaoId})
            return True
        except Exception as e:
            print(f"❌ Erro ao remover o arquivo: {e}")
            return False

    async def buscar_por_solicitacao_id(self, solicitacaoId: int) -> list[dict]:
        try:
            return await self.__db.arquivos.find({"solicitacaoId": solicitacaoId}).to_list(length=None)
        except Exception as e:
            print(f"❌ Erro ao buscar por solicitacaoId: {e}")
            return []