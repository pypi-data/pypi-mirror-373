# botrun_drive_manager.py
# 波通鑑生成 .botrun google doc 模板專用
import argparse
import os
import time
from typing import Any, Dict
from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

from botrun_ask_folder.translations import set_language


def authenticate_google_services(service_account_file: str):
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=[
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/documents",
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )
    drive_service = build("drive", "v3", credentials=credentials)
    docs_service = build("docs", "v1", credentials=credentials)
    return drive_service, docs_service


def authenticate_google_sheet_service(service_account_file: str):
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    sheet_service = build("sheets", "v4", credentials=credentials)
    return sheet_service


def replace_string_in_template(
    docs_service: Resource,
    document_id: str,
    new_collection_name: str,
    botrun_name_no_extension: str,
):
    requests = [
        {
            "replaceAllText": {
                "containsText": {
                    "text": "1IpnZVKecvjcPOsH0q6YyhpS2ek2-Eig9",
                    "matchCase": "true",
                },
                "replaceText": new_collection_name,
            }
        },
        {
            "replaceAllText": {
                "containsText": {
                    "text": "波通鑑人模板",
                    "matchCase": "true",
                },
                "replaceText": botrun_name_no_extension,
            }
        },
    ]
    docs_service.documents().batchUpdate(
        documentId=document_id, body={"requests": requests}
    ).execute()


def copy_template_to_new_document(
    drive_service: Resource,
    docs_service: Resource,
    parent_folder_id: str,
    file_name: str,
    template_file_id: str,
    new_collection_name: str,
) -> Dict[str, Any]:
    # 複製模板文件到指定資料夾
    file_metadata = {
        "name": file_name,
        "parents": [parent_folder_id],
    }
    copied_file = (
        drive_service.files()
        .copy(fileId=template_file_id, body=file_metadata, fields="id")
        .execute()
    )
    new_file_id = copied_file.get("id")

    # 更新新創建的 Google Docs 文件內容
    file_name_no_extension = file_name.split(".")[0]
    replace_string_in_template(
        docs_service, new_file_id, new_collection_name, file_name_no_extension
    )

    return copied_file


def check_and_manage_file_bak(
    drive_service: Resource,
    docs_service: Resource,
    parent_folder_id: str,
    botrun_file_name: str,
    template_file_id: str,
    collection_name: str,
):
    if not botrun_file_name.endswith(".botrun"):
        botrun_file_name += ".botrun"
    query = f"'{parent_folder_id}' in parents and name = '{botrun_file_name}'"
    results = (
        drive_service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
    )
    files = results.get("files", [])
    if not files:
        new_file = copy_template_to_new_document(
            drive_service,
            docs_service,
            parent_folder_id,
            botrun_file_name,
            template_file_id,
            collection_name,
        )
    print(
        f"""點連結編輯波特人:\n@begin link("https://drive.google.com/open?id={new_file["id"]}") {botrun_file_name} @end"""
    )


def check_and_manage_file(
    drive_service: Resource,
    docs_service: Resource,
    parent_folder_id: str,
    botrun_file_name: str,
    template_file_id: str,
    collection_name: str,
    force=False,
    lang="zh-TW",
):
    set_language(lang)
    if not botrun_file_name.endswith(".botrun"):
        botrun_file_name += ".botrun"
    query = f"'{parent_folder_id}' in parents and name = '{botrun_file_name}'"
    results = (
        drive_service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
    )
    files = results.get("files", [])
    if files and not force:
        file_id = files[0]["id"]
    elif files and force:
        delete_document(drive_service, files[0]["id"])
        new_file = copy_template_to_new_document(
            drive_service,
            docs_service,
            parent_folder_id,
            botrun_file_name,
            template_file_id,
            collection_name,
        )
        file_id = new_file["id"]
    else:
        new_file = copy_template_to_new_document(
            drive_service,
            docs_service,
            parent_folder_id,
            botrun_file_name,
            template_file_id,
            collection_name,
        )
        file_id = new_file["id"]
    if lang == "zh-TW":
        print(
            f"""@begin link("https://docs.google.com/document/d/{file_id}/edit") \n🤖編輯波特人: {botrun_file_name}\n @end"""
        )
        print(f"""@begin button("呼叫波特人"){botrun_file_name[:-7]}@end""")
    else:
        print(
            f"""@begin link("https://docs.google.com/document/d/{file_id}/edit") \n🤖Edit Bot Wiki: {botrun_file_name}\n @end"""
        )
        print(f"""@begin button("Launch Bot Wiki"){botrun_file_name[:-7]}@end""")


DEFAULT_SERVICE_ACCOUNT_FILE = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS", "./keys/google_service_account_key.json"
)
DEFAULT_PARENT_FOLDER_ID = os.getenv(
    "GOOGLE_DRIVE_BOTS_FOLDER_ID", "1pMG5KOdYtYVvyKEkdfxpcawpUPKPp-cp"
)
DEFAULT_TEMPLATE_FILE_ID = os.getenv(
    "BOTRUN_DEFAULT_TEMPLATE_FILE_ID", "1PPoC_E_P6HhhJBXBKnsRPwrYAkNQ8MNlSi_dEuxzayg"
)
DEFAULT_TEMPLATE_FILE_ID_EN = os.getenv(
    "BOTRUN_DEFAULT_TEMPLATE_FILE_ID_EN", "14KN43Nz3um28fOL9nFL4AlfJjojTrnMTQItJK4Uflu4"
)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Manage BotRun files in Google Drive.")
    parser.add_argument(
        "--botrun_file_name",
        default="波通鑑人1.botrun",
        help="The name of the botrun file to manage.",
    )
    parser.add_argument(
        "--collection_name", default="1PPoC_E_P6HhhJBXBKnsRPwrYAkNQ8MNlSi_dEuxzayg"
    )
    parser.add_argument("--parent_folder_id", default=DEFAULT_PARENT_FOLDER_ID)
    parser.add_argument("--service_account_file", default=DEFAULT_SERVICE_ACCOUNT_FILE)
    parser.add_argument("--template_file_id", default=DEFAULT_TEMPLATE_FILE_ID)
    return parser.parse_args()


def botrun_drive_manager(botrun_file_name, collection_name, force=False, lang="zh-TW"):
    drive_service, docs_service = authenticate_google_services(
        DEFAULT_SERVICE_ACCOUNT_FILE
    )
    if lang == "en":
        template_file_id = DEFAULT_TEMPLATE_FILE_ID_EN
    else:
        template_file_id = DEFAULT_TEMPLATE_FILE_ID
    check_and_manage_file(
        drive_service,
        docs_service,
        DEFAULT_PARENT_FOLDER_ID,
        botrun_file_name,
        template_file_id,
        collection_name,
        force=force,
        lang=lang,
    )


def list_folders(service, folder_id):
    """List all folders within the specified folder ID"""
    query = (
        f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])
    return folders


def get_folder_structure(service, folder_id, base_path=""):
    """Recursively get the folder structure"""
    folders = list_folders(service, folder_id)
    structure = {}
    for folder in folders:
        path = f"{folder['name']}" if base_path else folder["name"]
        structure[path] = get_folder_structure(service, folder["id"], path)
    return structure


def create_folder(service, name, parent_id):
    """Create a folder in the specified parent folder"""
    file_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=file_metadata, fields="id").execute()
    return folder["id"]


def ensure_folder_exists(service, name, parent_id):
    """Ensure the folder exists, if not, create it"""
    query = f"name='{name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])
    if not folders:
        return create_folder(service, name, parent_id)
    return folders[0]["id"]


def recreate_structure(
    service, structure, parent_id, return_structure=None, base_folder=""
):
    if return_structure is None:
        return_structure = {}

    """ Recursively recreate the directory structure """
    for folder_name, sub_structure in structure.items():
        folder_id = ensure_folder_exists(service, folder_name, parent_id)
        return_structure[f"{base_folder}{folder_name}/"] = folder_id
        new_base_folder = f"{base_folder}{folder_name}/"
        recreate_structure(
            service, sub_structure, folder_id, return_structure, new_base_folder
        )


def append_new_row_to_google_sheet(
    service, google_doc_id: str, worksheet_name: str, row_data
):
    range_name = worksheet_name  # 指定要添加數據的工作表名稱

    # 要添加的新行數據
    values = [row_data]  # 這行數據將被添加到新的一行中
    body = {"values": values}

    # 使用 Sheets API 的 append 方法來添加數據
    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=google_doc_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
            insertDataOption="INSERT_ROWS",
        )
        .execute()
    )


def search_files_in_folder(service, folder_id, keywords="", max_retries=3):
    try:
        # 定義查詢參數
        if keywords:
            # 用逗號和空白分隔關鍵字，去除重複的空白和逗號
            keywords = keywords.replace(",", " ").split()
            lst_keywords = [kw.strip() for kw in keywords if kw.strip()]
        else:
            lst_keywords = []

        if len(lst_keywords) > 1:
            keyword_queries = " or ".join(
                [f"name contains '{kw}'" for kw in lst_keywords]
            )
            query = (
                f"'{folder_id}' in parents and ({keyword_queries}) and trashed = false"
            )
        elif len(lst_keywords) == 1 and lst_keywords[0] != "":
            query = f"'{folder_id}' in parents and name contains '{lst_keywords[0]}' and trashed = false"
        else:
            query = f"'{folder_id}' in parents and trashed = false"

        attempt = 0
        # 呼叫 Drive API 進行搜尋
        while attempt < max_retries:
            try:
                # 呼叫 Drive API 進行搜尋
                results = (
                    service.files()
                    .list(
                        q=query,
                        spaces="drive",
                        fields="nextPageToken, files(id, name, mimeType)",
                        pageToken=None,
                    )
                    .execute()
                )

                items = results.get("files", [])

                if not items:
                    print("No files found.")
                    return []

                # 回傳搜尋到的檔案清單
                return items

            except HttpError as error:
                # print(f'An error occurred (attempt {attempt + 1}/{max_retries}): {error}')
                attempt += 1
                if attempt < max_retries:
                    # print('Retrying...')
                    time.sleep(2)

        print("Failed to search file after several retries.")
        return []

    except HttpError as error:
        print(f"Failed to search file: {error}")
        return []


def delete_document(drive_service, document_id):
    """
    Deletes a Google Docs document by its ID.

    Args:
        drive_service (Resource): The authenticated Google Drive service.
        document_id (str): The ID of the document to delete.
    """
    try:
        drive_service.files().delete(fileId=document_id).execute()
        print(f"Document with ID {document_id} has been deleted.")
    except HttpError as error:
        print(f"An error occurred: {error}")


def main():
    args = parse_arguments()
    drive_service, docs_service = authenticate_google_services(
        args.service_account_file
    )
    check_and_manage_file(
        drive_service,
        docs_service,
        args.parent_folder_id,
        args.botrun_file_name,
        args.template_file_id,
        args.collection_name,
    )


if __name__ == "__main__":
    main()
"""
source venv/bin/activate
python ./lib_botrun/botrun_ask_folder/botrun_drive_manager.py
"""
