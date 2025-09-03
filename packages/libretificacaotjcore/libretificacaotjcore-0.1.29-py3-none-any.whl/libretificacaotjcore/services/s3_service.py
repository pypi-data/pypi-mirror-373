import asyncio
from functools import partial
import os
import boto3
from botocore.exceptions import ClientError

class S3Service:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name, bucket_name, bucket_path):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        
        self.bucket_name = bucket_name
        self.bucket_path = bucket_path

        self.loop = asyncio.get_running_loop()

    async def save_on_s3(self, file_path, file_name):
        try:
            await self.loop.run_in_executor(
                None,
                self.s3.upload_file,
                file_path,
                self.bucket_name,
                self.bucket_path + file_name,
            )
        except Exception as e:
            print(f"❌ Erro ao salvar o arquivo no S3: {e}")

    async def save_many_paths_on_s3(self, file_paths):
        """
        Salva vários arquivos no S3 informando apenas os caminhos locais.
        O nome do arquivo no S3 será o mesmo do arquivo local.
        """
        tasks = [
            self.save_on_s3(
                file_path["caminho_arquivo_local"], file_path["nome_arquivo"]
            )
            for file_path in file_paths
        ]
        await asyncio.gather(*tasks)

    async def file_on_s3(self, file_name):
        try:
            head_object_func = partial(
                self.s3.head_object,
                Bucket=self.bucket_name,
                Key=self.bucket_path + file_name,
            )

            await self.loop.run_in_executor(None, head_object_func)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False

            raise
        except Exception as e:
            print(f"❌ Erro ao obter o arquivo do S3: {e}")
            return False

    async def get_file_from_s3(self, file_name, destination_path):
        try:
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

            key = self.bucket_path + file_name
            print(f"🔍 Verificando chave: {key}")
            download_func = partial(
                self.s3.download_file, self.bucket_name, key, destination_path
            )

            await self.loop.run_in_executor(None, download_func)
            print(f"📖✅ Arquivo '{file_name}' baixado com sucesso.")
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print(f"⚠️ Arquivo '{file_name}' não encontrado no S3.")
            else:
                print(f"❌ Erro ao baixar o arquivo do S3: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado ao baixar o arquivo do S3: {e}")
