import aiohttp
import os
from typing import List, Union
from botrun_ask_folder.constants import FAST_API_TIMEOUT
from botrun_ask_folder.fast_api.util.http_request_retry_decorator import async_retry
from botrun_ask_folder.models.drive_folder import DriveFolder
from botrun_ask_folder.models.drive_file import DriveFile, DriveFileStatus
from botrun_ask_folder.models.splitted_file import SplittedFile
from botrun_ask_folder.services.drive.drive_client import DriveClient
from dotenv import load_dotenv

load_dotenv()

API_PREFIX = "api/botrun/botrun_ask_folder"
BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN = os.getenv("BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN")


class FastAPIDriveClient(DriveClient):
    def __init__(self, api_url: str = os.getenv("BOTRUN_ASK_FOLDER_FAST_API_URL")):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN}"}

    @async_retry(attempts=3, delay=1)
    async def get_drive_folder(self, id: str) -> Union[DriveFolder, None]:
        print(
            f"[fast_api_drive_client][get_drive_folder] {self.api_url}/{API_PREFIX}/drive_folder/{id}"
        )
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/{API_PREFIX}/drive_folder/{id}",
                    headers=self.headers,
                    timeout=FAST_API_TIMEOUT,
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return DriveFolder(**data)
        except Exception as e:
            print(f"FastAPIDriveClient Error getting drive folder {id}: {e}")
            return None

    @async_retry(attempts=3, delay=1)
    async def set_drive_folder(self, folder: DriveFolder) -> DriveFolder:
        print(
            f"[fast_api_drive_client][set_drive_folder] {self.api_url}/{API_PREFIX}/drive_folder"
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/drive_folder",
                json=folder.model_dump(),
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                print(f"set_drive_folder get response {data}")
                return DriveFolder(**data["drive_folder"])

    @async_retry(attempts=3, delay=1)
    async def delete_drive_folder(self, id: str) -> bool:
        print(
            f"[fast_api_drive_client][delete_drive_folder] {self.api_url}/{API_PREFIX}/drive_folder/{id}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.api_url}/{API_PREFIX}/drive_folder/{id}",
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["message"] == "Status deleted successfully"

    # @async_retry(attempts=3, delay=1)
    # async def update_drive_file_status_in_folder(
    #     self, folder_id: str, file_id: str, new_status: DriveFileStatus
    # ):
    #     async with aiohttp.ClientSession() as session:
    #         print(
    #             f"fast_api_drive_client update_drive_file_status_in_folder {file_id} Updating file status in folder {folder_id} to {new_status.value}"
    #         )
    #         async with session.post(
    #             f"{self.api_url}/{API_PREFIX}/drive_folder/{folder_id}/update_file_status",
    #             json={"file_id": file_id, "new_status": new_status.value},
    #             headers=self.headers,
    #             timeout=FAST_API_TIMEOUT,
    #         ) as response:
    #             response.raise_for_status()
    #             data = await response.json()
    #             return data

    @async_retry(attempts=3, delay=1)
    async def get_drive_file(self, id: str) -> Union[DriveFile, None]:
        try:
            print(
                f"[fast_api_drive_client][get_drive_file] {self.api_url}/{API_PREFIX}/drive_file/{id}"
            )
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/{API_PREFIX}/drive_file/{id}",
                    headers=self.headers,
                    timeout=FAST_API_TIMEOUT,
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return DriveFile(**data)
        except Exception as e:
            print(f"FastAPIDriveClient Error getting drive file {id}: {e}")
            return None

    @async_retry(attempts=3, delay=1)
    async def set_drive_file(self, file: DriveFile) -> DriveFile:
        print(
            f"[fast_api_drive_client] [set_drive_file] {self.api_url}/{API_PREFIX}/drive_file"
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/drive_file",
                json=file.model_dump(),
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return DriveFile(**data["drive_file"])

    @async_retry(attempts=3, delay=1)
    async def delete_drive_file(self, id: str) -> bool:
        print(
            f"[fast_api_drive_client][delete_drive_file] {self.api_url}/{API_PREFIX}/drive_file/{id}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.api_url}/{API_PREFIX}/drive_file/{id}",
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["message"] == "File deleted successfully"

    @async_retry(attempts=3, delay=1)
    async def get_splitted_file(self, id: str) -> Union[SplittedFile, None]:
        try:
            print(
                f"[fast_api_drive_client][get_splitted_file] {self.api_url}/{API_PREFIX}/splitted_file/{id}"
            )
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/{API_PREFIX}/splitted_file/{id}",
                    headers=self.headers,
                    timeout=FAST_API_TIMEOUT,
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return SplittedFile(**data)
        except Exception as e:
            print(f"FastAPIDriveClient Error getting splitted file {id}: {e}")
            return None

    @async_retry(attempts=3, delay=1)
    async def set_splitted_file(self, file: SplittedFile) -> SplittedFile:
        print(
            f"[fast_api_drive_client] [set_splitted_file] {self.api_url}/{API_PREFIX}/splitted_file"
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/splitted_file",
                json=file.model_dump(),
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return SplittedFile(**data["splitted_file"])

    @async_retry(attempts=3, delay=1)
    async def delete_splitted_file(self, id: str) -> bool:
        print(
            f"[fast_api_drive_client][delete_splitted_file] {self.api_url}/{API_PREFIX}/splitted_file/{id}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.api_url}/{API_PREFIX}/splitted_file/{id}",
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["message"] == "Splitted file deleted successfully"

    @async_retry(attempts=3, delay=1)
    async def update_drive_files(self, folder_id: str, new_files: List[DriveFile]):
        print(
            f"[fast_api_drive_client][update_drive_files] {self.api_url}/{API_PREFIX}/drive_folder/{folder_id}/update_files"
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/drive_folder/{folder_id}/update_files",
                json=[file.model_dump() for file in new_files],
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data

    @async_retry(attempts=3, delay=1)
    async def get_split_files(self, folder_id: str):
        print(
            f"[fast_api_drive_client][get_split_files] {self.api_url}/{API_PREFIX}/drive_folder/{folder_id}/split_files"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/{API_PREFIX}/drive_folder/{folder_id}/split_files",
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return {
                    name: SplittedFile(**file_data) for name, file_data in data.items()
                }

    @async_retry(attempts=3, delay=1)
    async def get_drive_files(self, folder_id: str) -> List[DriveFile]:
        print(
            f"[fast_api_drive_client][get_drive_files] {self.api_url}/{API_PREFIX}/drive_folder/{folder_id}/files"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/{API_PREFIX}/drive_folder/{folder_id}/files",
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return [DriveFile(**file_data) for file_data in data]

    @async_retry(attempts=3, delay=1)
    async def get_non_embedded_files_count(
        self, file_ids: List[str], batch_size: int = 30
    ) -> int:
        print(
            f"[fast_api_drive_client][get_non_embedded_files_count] {self.api_url}/{API_PREFIX}/drive_files/non_embedded_count"
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/drive_files/non_embedded_count",
                json={
                    "file_ids": file_ids,
                    "batch_size": batch_size,
                },  # 將 batch_size 加入 JSON 請求體
                headers=self.headers,
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["non_embedded_count"]
