import aiohttp
import os
from io import BytesIO
from typing import Optional
from urllib.parse import unquote
from botrun_ask_folder.constants import FAST_API_TIMEOUT
from botrun_ask_folder.fast_api.util.http_request_retry_decorator import async_retry
from botrun_ask_folder.services.storage.storage_client import StorageClient
from dotenv import load_dotenv

load_dotenv()

API_PREFIX = "api/botrun/botrun_ask_folder"
BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN = os.getenv("BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN")


class FastAPIStorageClient(StorageClient):
    def __init__(self, api_url: str = os.getenv("BOTRUN_ASK_FOLDER_FAST_API_URL")):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN}"}

    @async_retry(attempts=3, delay=1)
    async def store_file(self, filepath: str, file_object: BytesIO) -> bool:
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field("file", file_object, filename=os.path.basename(filepath))
            encoded_filepath = unquote(filepath)
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/storage?filepath={encoded_filepath}",
                data=form,
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["message"] == "File uploaded successfully"

    @async_retry(attempts=3, delay=1)
    async def retrieve_file(self, filepath: str) -> Optional[BytesIO]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/{API_PREFIX}/storage/{filepath}",
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                content = await response.read()
                return BytesIO(content)

    @async_retry(attempts=3, delay=1)
    async def delete_file(self, filepath: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.api_url}/{API_PREFIX}/storage/{filepath}",
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                if response.status == 404:
                    return False
                response.raise_for_status()
                data = await response.json()
                return data["message"] == "File deleted successfully"

    @async_retry(attempts=3, delay=1)
    async def file_exists(self, filepath: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/{API_PREFIX}/storage/{filepath}/exists",
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["exists"]
