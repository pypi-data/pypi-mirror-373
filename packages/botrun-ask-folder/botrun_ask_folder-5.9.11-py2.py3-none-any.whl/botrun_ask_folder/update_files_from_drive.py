import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import Resource
from typing import List, Dict
from botrun_ask_folder.botrun_ask_folder import (
    handle_downloaded_files_and_save_to_qdrant,
    botrun_ask_folder,
)
from botrun_ask_folder.drive_download import (
    download_file,
    truncate_filename,
    drive_download_items,
)
from botrun_ask_folder.drive_download_metadata import update_drive_download_metadata
from botrun_ask_folder.models.google_drive_file_update_info import (
    GoogleDriveFileUpdateInfo,
    GoogleDriveFileUpdateResponse,
)
from pathlib import Path


def update_files_from_drive(
    data_list: List[Dict],
    data_path: Path,
) -> List[GoogleDriveFileUpdateResponse]:
    """
    :param data_list: List of dictionaries containing file information，可以轉成GoogleDriveFileUpdateInfo
    """
    file_info_list = GoogleDriveFileUpdateInfo.from_list(data_list)
    service_account_file = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS", "./keys/google_service_account_key.json"
    )
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file
    )
    service = build("drive", "v3", credentials=credentials)
    lst_response = []
    for file_info in file_info_list:
        if file_info.file_id != "":
            # 原有的處理邏輯
            file_metadata = (
                service.files()
                .get(
                    fileId=file_info.file_id,
                    fields="id, name, size, mimeType, parents, modifiedTime",
                )
                .execute()
            )
            output_folder = str(data_path / file_info.collection_id)
            file_metadata["path"] = file_metadata["name"]
            new_items = drive_download_items(
                service_account_file, [file_metadata], output_folder
            )
            if len(new_items) > 0:
                update_drive_download_metadata(new_items, output_folder)

            handle_downloaded_files_and_save_to_qdrant(
                file_info.collection_id, new_items=new_items
            )
            lst_response.append(
                GoogleDriveFileUpdateResponse(
                    file_id=file_info.file_id,
                    file_modified_time=file_metadata["modifiedTime"],
                )
            )
        else:
            # 需要更新整個 collection
            botrun_ask_folder(
                file_info.collection_id,
            )

    return lst_response
