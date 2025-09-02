from abc import ABC, abstractmethod
from typing import List, Union

from botrun_ask_folder.models.drive_folder import DriveFolder
from botrun_ask_folder.models.drive_file import DriveFile, DriveFileStatus
from botrun_ask_folder.models.splitted_file import SplittedFile


class DriveClient(ABC):
    @abstractmethod
    async def get_drive_folder(self, id: str) -> Union[DriveFolder, None]:
        pass

    @abstractmethod
    async def set_drive_folder(self, folder: DriveFolder) -> DriveFolder:
        pass

    @abstractmethod
    async def delete_drive_folder(self, id: str) -> bool:
        pass

    # @abstractmethod
    # async def update_drive_file_status_in_folder(
    #     self, folder_id: str, file_id: str, new_status: DriveFileStatus
    # ):
    #     pass

    @abstractmethod
    async def get_drive_file(self, id: str) -> Union[DriveFile, None]:
        pass

    @abstractmethod
    async def set_drive_file(self, file: DriveFile) -> DriveFile:
        pass

    @abstractmethod
    async def delete_drive_file(self, id: str) -> bool:
        pass

    @abstractmethod
    async def get_splitted_file(self, id: str) -> Union[SplittedFile, None]:
        pass

    @abstractmethod
    async def set_splitted_file(self, file: SplittedFile) -> SplittedFile:
        pass

    @abstractmethod
    async def delete_splitted_file(self, id: str) -> bool:
        pass

    @abstractmethod
    async def update_drive_files(self, folder_id: str, new_files: List[DriveFile]):
        pass

    @abstractmethod
    async def get_split_files(self, folder_id: str):
        pass

    @abstractmethod
    async def get_drive_files(self, folder_id: str) -> List[DriveFile]:
        pass

    @abstractmethod
    async def get_non_embedded_files_count(
        self, file_ids: List[str], batch_size: int = 30
    ) -> int:
        pass
