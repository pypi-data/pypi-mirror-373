import asyncio
from io import BytesIO
import os
import shutil
from pathlib import Path
import zipfile
import aiofiles
import aiofiles.os

class FileService:
    async def zip_folder(self, folder_path: str, output_path: str):
        buffer = BytesIO()
        
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, folder_path)

                    async with aiofiles.open(full_path, "rb") as f:
                        content = await f.read()
                        zip_file.writestr(arcname, content)
        
        async with aiofiles.open(output_path, "wb") as f:
            await f.write(buffer.getvalue())
            
    async def extract_zip(self, folder_path_zip: str, output_path: str):
            if not await aiofiles.os.path.exists(folder_path_zip):
                raise FileNotFoundError(
                    f"Arquivo ZIP não encontrado: {folder_path_zip}"
                )

            if not await aiofiles.os.path.exists(output_path):
                await aiofiles.os.makedirs(output_path, exist_ok=True)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._extrair_zip, folder_path_zip, output_path
            )

    async def remove_file(self, file_path: str):
        if await aiofiles.os.path.exists(file_path):
            await aiofiles.os.remove(file_path)
            
    async def remove_folder(self, folder_path: str):
        if await aiofiles.os.path.exists(folder_path):
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, shutil.rmtree, folder_path)
            
    def _extrair_zip(self, folder_path_zip: str, output_path: str):
        with zipfile.ZipFile(folder_path_zip, "r") as zip_ref:
            zip_ref.extractall(output_path)
            