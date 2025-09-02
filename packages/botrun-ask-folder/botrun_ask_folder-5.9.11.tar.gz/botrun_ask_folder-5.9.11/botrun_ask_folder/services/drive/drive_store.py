from abc import ABC, abstractmethod
from typing import Union, List
from botrun_ask_folder.models.drive_folder import DriveFolder
from botrun_ask_folder.models.drive_file import DriveFile, DriveFileStatus
from botrun_ask_folder.models.splitted_file import SplittedFile

DRIVE_FOLDER_STORE_NAME = "drive-folder-store"
DRIVE_FILE_STORE_NAME = "drive-file-store"
SPLITTED_FILE_STORE_NAME = "splitted-file-store"


class DriveFolderStore(ABC):
    @abstractmethod
    async def get_drive_folder(self, item_id: str) -> Union[DriveFolder, None]:
        pass

    @abstractmethod
    async def set_drive_folder(self, item: DriveFolder):
        pass

    # @abstractmethod
    # async def update_drive_file_status_in_folder(
    #     self, folder_id: str, file_id: str, new_status: DriveFileStatus
    # ):
    #     """
    #     drive folder 裡面，會有很多的 drive file
    #     但是要知道目前 drive folder 處理到幾個 drive file 了，還要再做一次 drive file 的 query
    #     費時非常久，所以這邊用一個 function 來將 drive file的 status更新在 drive folder裡
    #     但是要注意，因為可能有多個 drive file 去更新同一個drive folder，所以要注意race condition
    #     我們在 firestore，是利用它的 atomic update (https://firebase.google.com/docs/firestore/manage-data/add-data#update_fields_in_nested_objects) ，只更新一個欄位，而不是更新整個 item
    #     """
    #     pass

    @abstractmethod
    async def delete_drive_folder(self, item_id: str):
        pass

    @staticmethod
    def get_drive_folder_store_key(item_id: str) -> str:
        return f"{DRIVE_FOLDER_STORE_NAME}:{item_id}"


class DriveFileStore(ABC):
    @abstractmethod
    async def get_drive_file(self, file_id: str) -> Union[DriveFile, None]:
        pass

    @abstractmethod
    async def set_drive_file(self, file: DriveFile):
        pass

    @abstractmethod
    async def delete_drive_file(self, file_id: str):
        pass

    @abstractmethod
    async def get_non_embedded_files_count(
        self, file_ids: List[str], batch_size: int = 30
    ) -> int:
        pass

    @staticmethod
    def get_drive_file_store_key(file_id: str) -> str:
        return f"{DRIVE_FILE_STORE_NAME}:{file_id}"


class SplittedFileStore(ABC):
    @abstractmethod
    async def get_splitted_file(
        self, splitted_file_id: str
    ) -> Union[SplittedFile, None]:
        pass

    @abstractmethod
    async def set_splitted_file(self, file: SplittedFile):
        pass

    @abstractmethod
    async def delete_splitted_file(self, splitted_file_id: str):
        pass

    @staticmethod
    def get_splitted_file_store_key(splitted_file_id: str) -> str:
        return f"{SPLITTED_FILE_STORE_NAME}:{splitted_file_id}"
