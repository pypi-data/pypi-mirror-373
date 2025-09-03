from pymongo.errors import BulkWriteError

class CertificadoRepository:
    def __init__(self, db):
        self.__db = db

    async def inserir_certificado(self, certificado: dict) -> bool:
        try:
            certificado_no_db = await self.__db.certificado.find_one(
                {"cnpj": certificado["cnpj"]}
            )

            if certificado_no_db is None:
                await self.__db.certificado.insert_one(certificado)
                return True

            await self.__db.certificado.delete_one(
                {"cnpj": certificado["cnpj"]}
            )
            await self.__db.certificado.insert_one(certificado)
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir o arquivo: {e}")
            return False

    async def remover_certificado(self, cnpj: str) -> bool:
        try:
            await self.__db.certificado.delete_many({"cnpj": cnpj})
            return True
        except Exception as e:
            print(f"❌ Erro ao remover o certificado: {e}")
            return False

    async def buscar_certificado_por_cnpj(self, cnpj: str) -> list[dict]:
        try:
            return await self.__db.certificado.find({"cnpj": cnpj}).to_list(length=None)
        except Exception as e:
            print(f"❌ Erro ao buscar certificado: {e}")
            return []