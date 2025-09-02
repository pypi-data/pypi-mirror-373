import argparse
from io import BytesIO
import os
import shutil
from datetime import datetime, timezone
from typing import Union

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import Resource

from botrun_ask_folder.models.drive_file import DriveFile, DriveFileStatus

from .drive_list_files import drive_list_files_with_service
from .emoji_progress_bar import EmojiProgressBar
from .drive_download_metadata import (
    save_drive_download_metadata,
    update_drive_download_metadata,
)

from botrun_ask_folder.services.storage.storage_factory import storage_client_factory
from botrun_ask_folder.services.storage.storage_client import StorageClient


def truncate_filename(file_path: str, max_length: int = 80) -> str:
    directory, filename = os.path.split(file_path)
    if len(filename) > max_length:
        name, extension = os.path.splitext(filename)
        if len(extension) <= 4:
            # 如果副檔名長度小於等於4，保留副檔名
            truncated_name = name[: max_length - len(extension) - 1]
            filename = f"{truncated_name}{extension}"
        else:
            # 如果副檔名長度大於4，視為檔名的一部分，整個截斷
            filename = filename[:max_length]
        file_path = os.path.join(directory, filename)
    return file_path


def convert_google_apps_mime_to_office_mime(mime_type: str) -> Union[str, None]:
    mime_mapping = {
        "application/vnd.google-apps.document": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.google-apps.presentation": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
    return mime_mapping.get(mime_type, None)


def download_file(
    service: Resource, file_id: str, file_path: str, modified_time: str, mime_type: str
) -> Union[str, None]:
    try:
        file_path = truncate_filename(file_path)
        file_path = append_export_extension_to_path(file_path, mime_type)
        export_mime = convert_google_apps_mime_to_office_mime(mime_type)
        if export_mime:
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
        else:
            request = service.files().get_media(fileId=file_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        modified_time = datetime.strptime(
            modified_time, "%Y-%m-%dT%H:%M:%S.%fZ"
        ).replace(tzinfo=timezone.utc)
        mod_time_stamp = modified_time.timestamp()
        os.utime(file_path, (mod_time_stamp, mod_time_stamp))
        return file_path
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(
            f"drive_download.py, an error occurred while downloading the file: {file_path}"
        )
        print(f"error: {e}")


def append_file_extension(file_path: str, mime_type: str) -> str:
    extensions = {
        "application/vnd.google-apps.document": ".docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/vnd.google-apps.spreadsheet": ".xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "application/vnd.google-apps.presentation": ".pptx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    }
    for mimetype, ext in extensions.items():
        if mimetype == mime_type and file_path.endswith(ext):
            return file_path
    return file_path + extensions.get(mime_type, "")


def file_exist(file_path: str, mime_type: str) -> bool:
    updated_file_path = append_file_extension(file_path, mime_type)
    return os.path.exists(updated_file_path)


def append_export_extension_to_path(local_path: str, mime_type: str) -> str:
    return append_file_extension(local_path, mime_type)


def modified_time_match(local_path: str, drive_time: str, mime_type: str) -> bool:
    local_path = append_export_extension_to_path(local_path, mime_type)
    if not os.path.exists(local_path):
        return False
    local_mtime = datetime.fromtimestamp(os.path.getmtime(local_path), tz=timezone.utc)
    drive_mtime = datetime.strptime(drive_time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )
    local_mtime = local_mtime.replace(microsecond=0)
    drive_mtime = drive_mtime.replace(microsecond=0)
    return local_mtime == drive_mtime


def drive_download(
    service_account_file: str,
    parent_folder_id: str,
    max_files: int,
    output_folder: str = "./data",
    force: bool = False,
) -> list:
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file
    )
    service = build("drive", "v3", credentials=credentials)
    return drive_download_with_service(
        service, parent_folder_id, max_files, output_folder, force
    )


def drive_download_with_service(
    service,
    parent_folder_id: str,
    max_files: int,
    output_folder: str = "./data",
    force: bool = False,
) -> list:
    print("== Begin listing files in Google Drive ==")
    dic_result = drive_list_files_with_service(service, parent_folder_id, max_files)
    items = dic_result["items"]
    new_items = drive_download_items_with_service(service, items, output_folder, force)
    drive_files = [item["name"] for item in items]
    downloaded_files = [item["name"] for item in new_items]
    if set(drive_files) == set(downloaded_files):
        # 表示第一次下載，要把完整的資料夾結構存下來
        save_drive_download_metadata(dic_result, output_folder)
        # Initialize and save CollectionStatus
        # init_drive_folder(dic_result)
    elif len(new_items) > 0:
        # 表示有部分檔案已載過，只需要更新 metadata
        update_drive_download_metadata(new_items, output_folder)
        # update_new_items_to_drive_folder(dic_result["parent_id"], new_items)
    return new_items


def drive_download_items(
    service_account_file, items, output_folder, force: bool = False
) -> list:
    print("== Begin downloading files from Google Drive ==")
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file
    )
    service = build("drive", "v3", credentials=credentials)
    return drive_download_items_with_service(service, items, output_folder, force)


def drive_download_items_with_service(
    service, items, output_folder, force: bool = False
) -> list:
    progress_bar = EmojiProgressBar(len(items))
    current_progress = 0

    download_count = 0
    skip_count = 0
    total_bytes = 0
    new_items = []
    for item in items:
        file_path = os.path.join(output_folder, item["path"])
        file_path = truncate_filename(file_path)
        if (
            not force
            and file_exist(file_path, item["mimeType"])
            and modified_time_match(file_path, item["modifiedTime"], item["mimeType"])
        ):
            skip_count += 1
            current_progress += 1
            progress_bar.update(current_progress)
            continue
        new_items.append(item)
        file_path = download_file(
            service, item["id"], file_path, item["modifiedTime"], item["mimeType"]
        )

        if file_path is not None:
            file_path_txts = f"{file_path}.txts"
            try:
                shutil.rmtree(file_path_txts)
            except FileNotFoundError:
                pass

        download_count += 1
        current_progress += 1
        progress_bar.update(current_progress)
        total_bytes += int(item["size"])

    print(
        f"Downloaded {download_count} files, total: {total_bytes} bytes, skipped {skip_count} files."
    )
    return new_items


def file_download_with_service(
    service, drive_file: DriveFile, output_folder, force: bool = False
) -> DriveFile:
    """
    這裡給 queue，下載單一檔案 使用的
    """
    # todo implement force
    os.makedirs(os.path.dirname(output_folder), exist_ok=True)
    file_path = os.path.join(output_folder, drive_file.folder_id, drive_file.path)
    file_path = truncate_filename(file_path)
    file_path = download_file(
        service, drive_file.id, file_path, drive_file.modifiedTime, drive_file.mimeType
    )

    if file_path is not None:
        file_path_txts = f"{file_path}.txts"
        try:
            shutil.rmtree(file_path_txts)
        except FileNotFoundError:
            pass
    drive_file.save_path = file_path
    drive_file.status = DriveFileStatus.DOWNLOADED
    return drive_file


async def drive_download_items_by_storage(
    service_account_file: str, items: list, drive_folder_id: str, force: bool = False
) -> list:
    print("== Begin downloading files from Google Drive using StorageClient ==")
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file
    )
    service = build("drive", "v3", credentials=credentials)

    storage_client: StorageClient = storage_client_factory()

    progress_bar = EmojiProgressBar(len(items))
    current_progress = 0

    download_count = 0
    total_bytes = 0
    new_items = []

    for item in items:
        file_path = f"{drive_folder_id}/{item['path']}"
        file_path = append_export_extension_to_path(file_path, item["mimeType"])

        new_items.append(item)

        export_mime = convert_google_apps_mime_to_office_mime(item["mimeType"])
        if export_mime:
            request = service.files().export_media(
                fileId=item["id"], mimeType=export_mime
            )
        else:
            request = service.files().get_media(fileId=item["id"])

        file_content = BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        file_content.seek(0)
        success = await storage_client.store_file(file_path, file_content)

        if success:
            download_count += 1
            total_bytes += int(item["size"])

            # Remove .txts file if it exists
            # txts_file_path = f"{file_path}.txts"
            # await storage_client.delete_file(txts_file_path)

        current_progress += 1
        progress_bar.update(current_progress)

    print(f"Downloaded {download_count} files, total: {total_bytes} bytes.")
    return new_items


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download files from Google Drive.")
    parser.add_argument(
        "--service_account_file",
        required=True,
        type=str,
        help="Path to the service account credentials file.",
    )
    parser.add_argument(
        "--parent_folder_id",
        required=True,
        type=str,
        help="ID of the Google Drive folder to download contents from.",
    )
    parser.add_argument(
        "--max_files",
        type=int,
        default=None,
        help="Maximum number of files to download.",
    )
    parser.add_argument(
        "--output_folder",
        type=str,
        default="./data/農業部20240224",
        help="Output folder for downloaded files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force download even if the file exists locally.",
    )
    args = parser.parse_args()
    drive_download(
        args.service_account_file,
        args.parent_folder_id,
        args.max_files,
        args.output_folder,
        args.force,
    )

"""
source venv/bin/activate
python lib_botrun/botrun_ask_folder/drive_download.py \
--service_account_file "./keys/google_service_account_key.json" \
--parent_folder_id "1IpnZVKecvjcPOsH0q6YyhpS2ek2-Eig9" \
--output_folder "./data/1IpnZVKecvjcPOsH0q6YyhpS2ek2-Eig9"

"""
