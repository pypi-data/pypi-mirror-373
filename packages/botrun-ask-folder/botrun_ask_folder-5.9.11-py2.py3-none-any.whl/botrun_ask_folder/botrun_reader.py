import re
import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError


def read_botrun_content(botrun_name: str, folder_id: str) -> str:
    """
    從 Google Drive 的指定資料夾中讀取 .botrun 檔案的內容
    """
    try:
        # 建立 Google Drive API 客戶端
        service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        if not service_account_file:
            raise Exception(
                "GOOGLE_APPLICATION_CREDENTIALS environment variable is not set"
            )
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file
        )
        service = build("drive", "v3", credentials=credentials)

        # 搜尋 .botrun 檔案
        file_query = f"'{folder_id}' in parents and name='{botrun_name}.botrun'"
        file_results = (
            service.files()
            .list(q=file_query, spaces="drive", fields="files(id, mimeType)")
            .execute()
        )
        files = file_results.get("files", [])

        if not files:
            raise Exception(
                f"File '{botrun_name}.botrun' not found in the specified folder"
            )

        file_id = files[0]["id"]
        mime_type = files[0]["mimeType"]

        # 讀取檔案內容
        if mime_type == "application/vnd.google-apps.document":
            # 如果是 Google Docs 文件，使用 export 方法
            request = service.files().export_media(
                fileId=file_id, mimeType="text/plain"
            )
            file_content = request.execute()
            return file_content.decode("utf-8")
        else:
            # 對於其他類型的文件，使用 get_media 方法
            request = service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            done = False
            while done is False:
                _, done = downloader.next_chunk()
            return file_content.getvalue().decode("utf-8")

    except HttpError as error:
        raise Exception(f"An error occurred: {error}")


def extract_model_name(content: str) -> str:
    """
    從給定的字符串中提取模型名稱。
    模式為 "model=xx/xx" 或 "model=xx/xx/xx"，忽略大小寫和不可見字符。
    可以處理帶有 BOM 標記的文本。

    :param content: 包含模型名稱的字符串
    :return: 提取出的模型名稱，如果沒有找到則返回空字符串
    """
    # 修改正則表達式以匹配更多樣的模型名稱格式
    pattern = r"(?i)model\s*=\s*([\w.-]+(?:/[\w.-]+)*)"
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    return ""


def read_notice_prompt_and_collection_from_botrun(botrun_name, folder_id):
    """
    從 botrun 檔案讀取 notice_prompt 和 collection_name
    """
    # 這裡需要實現從 botrun 檔案讀取內容的邏輯
    # 以下是示例邏輯，您需要根據實際情況修改
    file_content = read_botrun_content(botrun_name, folder_id)
    # print(file_content)
    lines = file_content.split("\n")
    if len(lines) < 1:
        raise ValueError("這個文件裡面沒有內容")

    chat_model = "openai/gpt-4o-2024-08-06"
    tmp_model = extract_model_name(lines[0])
    if tmp_model != "":
        chat_model = tmp_model

    # 分割內容
    parts = file_content.split("@begin import_rag_plus")

    if len(parts) < 2:
        notice_prompt = parts[0].strip()
        return notice_prompt, None, chat_model
        # raise ValueError("無法"
        #                  "找到 @begin import_rag_plus 標記")

    notice_prompt = parts[0].strip()

    # 解析 JSON 部分以獲取 collection_name
    import json

    try:
        rag_config = json.loads(parts[1].split("@end")[0])
        collection_name = rag_config.get("collection_name")
        if not collection_name:
            raise ValueError("無法在 JSON 中找到 collection_name")
    except json.JSONDecodeError:
        raise ValueError("無法解析 JSON 配置")

    return notice_prompt, collection_name, chat_model
