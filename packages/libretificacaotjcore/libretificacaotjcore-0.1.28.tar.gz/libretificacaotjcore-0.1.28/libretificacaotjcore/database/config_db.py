import motor.motor_asyncio

class ConfigDb:
    def __init__(self, host: str, user: str, password: str, port: int, db_name: str):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.db_name = db_name
        
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            f"mongodb://{self.host}:{self.port}"
        )
        self.__db = self.client[self.db_name]
        self.db_initialized = False
        
        
    async def criar_schema(self):
        global _db_initialized
        if not self.db_initialized:
            if "arquivos" not in (await self.__db.list_collection_names()):
                await self.__db.create_collection("arquivos")
            
            await self.__db.arquivos.create_index([("cnpj", 1)])
            await self.__db.arquivos.create_index([("solicitacaoId", 1)])
            await self.__db.arquivos.create_index([("id", 1)], unique=True)
            await self.__db.arquivos.create_index([("solicitacaoId", 1), ("cpf", 1)], unique=True)
            self.db_initialized = True
            
            if "protocolos" not in (await self.__db.list_collection_names()):
                await self.__db.create_collection("protocolos")
            
            await self.__db.protocolos.create_index([("cnpj", 1)])
            await self.__db.protocolos.create_index([("solicitacaoId", 1)])
            await self.__db.protocolos.create_index([("id", 1)], unique=True)
            await self.__db.protocolos.create_index([("solicitacaoId", 1), ("evento", 1)], unique=True)
            self.db_initialized = True
            
    async def get_db(self):
        await self.criar_schema()
        return self.__db