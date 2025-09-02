import mimetypes
import os
import tempfile
from dotenv import load_dotenv
from botrun_hatch.models.hatch import Hatch
from botrun_hatch.models.upload_file import UploadFile
from google.cloud import firestore
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError, NotFound
from google.oauth2 import service_account
from io import BytesIO
from typing import Union, Optional
import logging

from botrun_ask_folder.util.file_handler import (
    FailedToExtractContentException,
    HandlePowerpointError,
    UnsupportedFileException,
    handle_file_upload,
)

load_dotenv()

HATCH_BUCKET_NAME = "hatch"
HATCH_STORE_NAME = "hatch"


class HatchFirestoreStore:
    def __init__(self, env_name: str):
        self.env_name = env_name
        collection_name = f"{self.env_name}-{HATCH_STORE_NAME}"

        google_service_account_key_path = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS_FOR_FASTAPI",
            "/app/keys/scoop-386004-d22d99a7afd9.json",
        )
        credentials = service_account.Credentials.from_service_account_file(
            google_service_account_key_path,
            scopes=["https://www.googleapis.com/auth/datastore"],
        )

        # 直接从环境变量获取项目 ID
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

        # 创建 Firestore 客户端，指定项目 ID（如果环境变量中有设置）
        if project_id:
            self.db = firestore.Client(project=project_id, credentials=credentials)
        else:
            self.db = firestore.Client(credentials=credentials)

        self.collection = self.db.collection(collection_name)

    async def get_hatch(self, item_id: str) -> Union[Hatch, None]:
        doc_ref = self.collection.document(item_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return Hatch(**data)
        else:
            print(f">============Getting hatch {item_id} not exists")
            return None


class StorageCloudStore:
    def __init__(self, env_name: str):
        self.env_name = env_name
        google_service_account_key_path = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS_FOR_FASTAPI",
            "/app/keys/scoop-386004-d22d99a7afd9.json",
        )
        credentials = service_account.Credentials.from_service_account_file(
            google_service_account_key_path,
            scopes=["https://www.googleapis.com/auth/devstorage.full_control"],
        )

        self.storage_client = storage.Client(credentials=credentials)
        self.bucket_name = f"{HATCH_BUCKET_NAME}-{self.env_name}"
        self.bucket = self.storage_client.bucket(self.bucket_name)

    async def get_file(self, user_id: str, file_id: str) -> Optional[BytesIO]:
        try:
            filepath = f"{user_id}/{file_id}"
            blob = self.bucket.blob(filepath)
            file_object = BytesIO()
            blob.download_to_file(file_object)
            file_object.seek(0)
            return file_object
        except NotFound:
            logging.error(f"File not found in Cloud Storage: {filepath}")
            return None
        except Exception as e:
            logging.error(f"Error retrieving file from Cloud Storage: {e}")
            return None


def hatch_store_factory() -> HatchFirestoreStore:
    env_name = os.getenv("HATCH_ENV_NAME", "botrun-hatch-dev")
    return HatchFirestoreStore(env_name)


def storage_store_factory() -> StorageCloudStore:
    env_name = os.getenv("HATCH_ENV_NAME", "botrun-hatch-dev")
    return StorageCloudStore(env_name)


async def read_notice_prompt_and_model_from_hatch(hatch_id):
    print(f"read_notice_prompt_and_collection_from_hatch: {hatch_id}")
    hatch_store = hatch_store_factory()
    hatch = await hatch_store.get_hatch(hatch_id)
    if hatch is None:
        raise Exception(f"Hatch {hatch_id} not found")
    system_prompt = hatch.prompt_template
    if len(hatch.files) > 0:
        embed_content = await process_all_files(hatch.user_id, hatch)
        system_prompt += embed_content

    return system_prompt, None, hatch.model_name


async def process_file(user_id: str, file: UploadFile):
    storage_client = storage_store_factory()
    temp_path = None
    try:
        # Get file content from storage
        file_data = await storage_client.get_file(user_id, file.id)
        if file_data:
            # Create temporary file with original filename
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, file.name)

            # Write content to temp file
            with open(temp_path, "wb") as temp_file:
                temp_file.write(file_data.getvalue())

            try:
                # Extract text content
                err, content = await get_doc_content(temp_path)
                if not err:
                    return f"檔名：\n{file.name}\n檔案內容：\n{content}\n\n"
                else:
                    print(f"Error extracting content from {file.name}: {err}")
            finally:
                # Clean up temporary file
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)
        else:
            print(f"Could not retrieve file {file.id} for user {user_id}")
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"Error processing file {file.name}: {str(e)}")
        # Make sure to clean up temp file even if an error occurs
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
    return f"檔名：\n{file.name}\n"


async def get_doc_content(file_path: str) -> tuple[str, str]:
    """獲取文件內容，並確保正確處理 MIME 類型"""
    file_name = os.path.basename(file_path)

    # 1. 先嘗試使用 mimetypes
    file_mime = mimetypes.guess_type(file_path)[0]

    # 2. 如果 mimetypes 返回 None，使用擴展名映射
    if file_mime is None:
        ext = os.path.splitext(file_path)[1].lower()
        mime_map = {
            ".txt": "text/plain",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".ppt": "application/vnd.ms-powerpoint",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".csv": "text/csv",
            ".json": "application/json",
            ".xml": "application/xml",
            ".html": "text/html",
            ".htm": "text/html",
        }
        file_mime = mime_map.get(ext)

    try:
        content = await handle_file_upload(file_name, file_path, file_mime)
        return "", content
    except UnsupportedFileException as e:
        return f"目前不支援這個檔案類型: {file_mime}", ""
    except FailedToExtractContentException as e:
        return f"無法從檔案 {file_name} 取得內容", ""
    except HandlePowerpointError as e:
        return f"無法處理 PowerPoint 文件: {str(e)}", ""


# Process all files concurrently
async def process_all_files(user_id: str, hatch: Hatch):
    results = []
    for file in hatch.files:
        result = await process_file(user_id, file)
        results.append(result)
    return "".join(results)
