from google.cloud import storage
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account
from io import BytesIO
import os

from botrun_ask_folder.services.storage.storage_store import StorageStore


class StorageCsStore(StorageStore):
    def __init__(self, bucket_name: str = "botrun_ask_folder"):
        google_service_account_key_path = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS_FOR_FASTAPI",
            "/app/keys/scoop-386004-d22d99a7afd9.json",
        )
        credentials = service_account.Credentials.from_service_account_file(
            google_service_account_key_path,
            scopes=["https://www.googleapis.com/auth/devstorage.read_write"],
        )

        self.storage_client = storage.Client(credentials=credentials)
        self.bucket_name = bucket_name
        self.bucket = self.storage_client.bucket(self.bucket_name)

    async def store_file(self, filepath: str, file_object: BytesIO) -> bool:
        try:
            blob = self.bucket.blob(filepath)
            blob.upload_from_file(file_object, rewind=True)
            return True
        except Exception as e:
            print(f"Error storing file in Cloud Storage: {e}")
            return False

    async def retrieve_file(self, filepath: str) -> BytesIO:
        try:
            blob = self.bucket.blob(filepath)
            file_object = BytesIO()
            blob.download_to_file(file_object)
            file_object.seek(0)  # Rewind the file object to the beginning
            return file_object
        except NotFound:
            print(f"File not found in Cloud Storage: {filepath}")
            return None
        except Exception as e:
            print(f"Error retrieving file from Cloud Storage: {e}")
            return None

    async def delete_file(self, filepath: str) -> bool:
        try:
            blob = self.bucket.blob(filepath)
            blob.delete()
            return True
        except NotFound:
            print(f"File not found in Cloud Storage: {filepath}")
            return False
        except Exception as e:
            print(f"Error deleting file from Cloud Storage: {e}")
            return False

    async def file_exists(self, filepath: str) -> bool:
        try:
            blob = self.bucket.blob(filepath)
            return blob.exists()
        except Exception as e:
            print(f"Error checking file existence in Cloud Storage: {e}")
            return False
