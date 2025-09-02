from pydantic import BaseModel
import json
import litellm
from botrun_ask_folder.constants import GENERAL_OPEN_AI_MODEL
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import os
from dotenv import load_dotenv

from botrun_ask_folder.models.reference import (
    GoogleFileReference,
    GoogleFileReferences,
    Reference,
    References,
)

load_dotenv()


class RagAction(BaseModel):
    is_kb: bool
    is_keyword: bool


def read_rag_action_prompt_from_google_doc():
    # 從 .env 文件中獲取 Google Doc ID
    doc_id = os.getenv("BOTRUN_RAG_ACTION_TEMPLATE_FILE_ID")
    if not doc_id:
        raise ValueError("BOTRUN_RAG_ACTION_TEMPLATE_FILE_ID not found in .env file")
    return read_prompt_from_google_doc(doc_id)


def read_rag_reference_prompt_from_google_doc():
    # 從 .env 文件中獲取 Google Doc ID
    doc_id = os.getenv("BOTRUN_RAG_REFERENCE_TEMPLATE_FILE_ID")
    if not doc_id:
        raise ValueError("BOTRUN_RAG_REFERENCE_TEMPLATE_FILE_ID not found in .env file")
    return read_prompt_from_google_doc(doc_id)


def read_prompt_from_google_doc(doc_id: str):
    service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    if not service_account_file:
        raise Exception(
            "GOOGLE_APPLICATION_CREDENTIALS environment variable is not set"
        )

    # 創建憑證
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )

    # 建立 Google Drive API 客戶端
    service = build("drive", "v3", credentials=credentials)

    try:
        # 獲取文件元數據
        file_metadata = service.files().get(fileId=doc_id, fields="mimeType").execute()
        mime_type = file_metadata["mimeType"]

        if mime_type == "application/vnd.google-apps.document":
            # 如果是 Google Docs 文件，使用 export 方法
            request = service.files().export_media(fileId=doc_id, mimeType="text/plain")
            file_content = request.execute()
            return file_content.decode("utf-8")
        else:
            # 對於其他類型的文件，使用 get_media 方法
            request = service.files().get_media(fileId=doc_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            done = False
            while done is False:
                _, done = downloader.next_chunk()
            return file_content.getvalue().decode("utf-8")

    except Exception as error:
        raise Exception(f"An error occurred while reading the document: {error}")


def get_rag_action(
    rag_action_prompt: str, user_input: str, system_message: str, bot_response: str
) -> RagAction:
    prompt = (
        rag_action_prompt.replace("{user_input}", user_input)
        .replace("{system_message}", system_message)
        .replace("{bot_response}", bot_response)
    )
    response = litellm.completion(
        model=GENERAL_OPEN_AI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that provides structured output.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return RagAction(**result)


def get_rag_references(
    rag_reference_prompt: str, user_input: str, system_message: str, bot_response: str
) -> References:
    try:
        prompt = (
            rag_reference_prompt.replace("{user_input}", user_input)
            .replace("{system_message}", system_message)
            .replace("{bot_response}", bot_response)
        )
        response = litellm.completion(
            model=GENERAL_OPEN_AI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides structured output.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        google_file_refs = GoogleFileReferences(**result)
        references = References()

        for reference in google_file_refs.references:
            if reference.file_name != "" and reference.file_id != "":
                references.references.append(
                    Reference(
                        file_name=reference.file_name,
                        file_link=f"https://drive.google.com/file/d/{reference.file_id}/view",
                        page_numbers=sorted(set(reference.page_numbers)),
                        sheet_names=reference.sheet_names,
                    )
                )
        return references
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"get_rag_references error: {e}")
        return References()
