from typing import Union, List
from botrun_ask_folder.models.drive_folder import DriveFolder
from botrun_ask_folder.models.drive_file import DriveFile, DriveFileStatus
from botrun_ask_folder.models.splitted_file import SplittedFile
from google.cloud import firestore
from google.oauth2 import service_account
import os
from google.cloud.exceptions import GoogleCloudError
from dotenv import load_dotenv

load_dotenv()

from botrun_ask_folder.services.drive.drive_store import (
    DRIVE_FILE_STORE_NAME,
    DRIVE_FOLDER_STORE_NAME,
    SPLITTED_FILE_STORE_NAME,
    DriveFolderStore,
    DriveFileStore,
    SplittedFileStore,
)


class FirestoreBase:
    def __init__(self, collection_name: str):
        google_service_account_key_path = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS_FOR_FASTAPI",
            "/app/keys/scoop-386004-d22d99a7afd9.json",
        )
        credentials = service_account.Credentials.from_service_account_file(
            google_service_account_key_path,
            scopes=["https://www.googleapis.com/auth/datastore"],
        )

        db = firestore.Client(credentials=credentials)
        self.collection = db.collection(collection_name)


class DriveFolderFsStore(DriveFolderStore, FirestoreBase):
    def __init__(self):
        super().__init__(DRIVE_FOLDER_STORE_NAME)

    async def get_drive_folder(self, item_id: str) -> Union[DriveFolder, None]:
        doc_ref = self.collection.document(item_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return DriveFolder(**data)
        else:
            print(f">============Getting item {item_id} not exists")
            return None
            # raise ValueError(f"No CollectionStatus found with id: {item_id}")

    async def set_drive_folder(self, item: DriveFolder):
        """
        Set a CollectionStatus item in Firestore.
        If the item exists, it will be overwritten; if not, it will be created.
        """
        try:
            item.refresh_timestamp()
            doc_ref = self.collection.document(item.id)
            doc_ref.set(item.model_dump())
            return True, item
        except GoogleCloudError as e:
            print(f"Error setting drive folder {item.id}: {e}")
            return False, None

    async def delete_drive_folder(self, item_id: str):
        """
        Delete a CollectionStatus item from Firestore.
        """
        try:
            doc_ref = self.collection.document(item_id)
            doc_ref.delete()
            return True
        except GoogleCloudError as e:
            print(f"Error deleting drive folder {item_id}: {e}")
            return False


class DriveFileFsStore(DriveFileStore, FirestoreBase):
    def __init__(self):
        super().__init__(DRIVE_FILE_STORE_NAME)

    async def get_drive_file(self, file_id: str) -> Union[DriveFile, None]:
        doc_ref = self.collection.document(file_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return DriveFile(**data)
        else:
            print(f">============Getting file {file_id} not exists")
            raise ValueError(f"No DriveFile found with id: {file_id}")

    async def set_drive_file(self, file: DriveFile):
        try:
            file.refresh_timestamp()
            doc_ref = self.collection.document(file.id)
            doc_ref.set(file.model_dump())
            return True, file
        except GoogleCloudError as e:
            print(f"Error setting drive file {file.id}: {e}")
            return False, None

    async def delete_drive_file(self, file_id: str):
        try:
            doc_ref = self.collection.document(file_id)
            doc_ref.delete()
            return True
        except GoogleCloudError as e:
            print(f"Error deleting drive file {file_id}: {e}")
            return False

    async def get_non_embedded_files_count(
        self, file_ids: List[str], batch_size: int = 30
    ) -> int:
        """
        Get the count of file IDs that are not in EMBEDDED status.

        :param file_ids: List of file IDs to check
        :param batch_size: The number of documents to check at once
        :return: The count of file IDs that are not in EMBEDDED status
        """
        print(f"[drive_fs_store][get_non_embedded_files_count] file_ids: {file_ids}")
        try:
            total_count = 0
            # Process files in batches
            for i in range(0, len(file_ids), batch_size):
                batch = file_ids[i : i + batch_size]

                # Create a query to get all files in the batch that are not EMBEDDED
                print(f"[drive_fs_store][get_non_embedded_files_count] batch: {batch}")
                query = self.collection.where("id", "in", batch).where(
                    "status", "!=", DriveFileStatus.EMBEDDED.value
                )

                # Get the count of documents matching the query
                count = query.count().get()[0][0].value
                print(f"[drive_fs_store][get_non_embedded_files_count] count: {count}")
                total_count += count

            return total_count
        except Exception as e:
            import traceback

            traceback.print_exc()
            print(
                f"[drive_fs_store][get_non_embedded_files_count]Error getting non embedded files count: {e}"
            )
            raise e


class SplittedFileFsStore(SplittedFileStore, FirestoreBase):
    def __init__(self):
        super().__init__(SPLITTED_FILE_STORE_NAME)

    async def get_splitted_file(
        self, splitted_file_id: str
    ) -> Union[SplittedFile, None]:
        doc_ref = self.collection.document(splitted_file_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return SplittedFile(**data)
        else:
            print(f">============Getting splitted file {splitted_file_id} not exists")
            raise ValueError(f"No SplittedFile found with id: {splitted_file_id}")

    async def set_splitted_file(self, file: SplittedFile):
        try:
            file.refresh_timestamp()
            doc_ref = self.collection.document(file.id)
            doc_ref.set(file.model_dump())
            return True, file
        except GoogleCloudError as e:
            print(f"Error setting splitted file {file.id}: {e}")
            return False, None

    async def delete_splitted_file(self, file_id: str):
        try:
            doc_ref = self.collection.document(file_id)
            doc_ref.delete()
            return True
        except GoogleCloudError as e:
            print(f"Error deleting splitted file {file_id}: {e}")
            return False
