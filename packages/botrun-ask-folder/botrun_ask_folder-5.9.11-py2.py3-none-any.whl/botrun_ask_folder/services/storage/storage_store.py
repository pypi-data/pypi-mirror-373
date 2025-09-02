from abc import ABC, abstractmethod
from typing import Optional
from io import BytesIO


class StorageStore(ABC):
    @abstractmethod
    async def store_file(self, filepath: str, file_object: BytesIO) -> bool:
        """
        Store a file in the storage.

        :param filepath: The path where the file should be stored
        :param file_object: The file object to be stored (BytesIO)
        :return: True if the file was successfully stored, False otherwise
        """
        pass

    @abstractmethod
    async def retrieve_file(self, filepath: str) -> Optional[BytesIO]:
        """
        Retrieve a file from the storage.

        :param filepath: The path of the file to retrieve
        :return: BytesIO object containing the file data if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete_file(self, filepath: str) -> bool:
        """
        Delete a file from the storage.

        :param filepath: The path of the file to delete
        :return: True if the file was successfully deleted, False otherwise
        """
        pass

    @abstractmethod
    async def file_exists(self, filepath: str) -> bool:
        """
        Check if a file exists in the storage.

        :param filepath: The path of the file to check
        :return: True if the file exists, False otherwise
        """
        pass
