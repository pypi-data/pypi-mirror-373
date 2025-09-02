import json
import os
import shutil
import uuid
import asyncio
import pytz
from datetime import datetime
from pathlib import Path
from typing import List

from botrun_ask_folder.models.rag_metadata import PAGE_NUMBER_NA, RagMetadata
from botrun_ask_folder.models.drive_folder import (
    DriveFolder,
    DriveFolderStatus,
)
from botrun_ask_folder.models.drive_file import DriveFile, DriveFileStatus
from botrun_ask_folder.services.drive.drive_factory import (
    drive_client_factory,
)
from botrun_ask_folder.models.splitted_file import SplittedFile


def save_drive_download_metadata(dic_item: dict, output_folder: str):
    """
    從 Google Drive 把檔案下載回來的時候，會先將 dic_item 儲存一份
    """
    folder_id = output_folder.split("/")[-1]
    # if folder is not exist, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    file_path = os.path.join(
        output_folder, "{folder_id}-metadata.json".format(folder_id=folder_id)
    )
    # save dict as json, utf-8
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dic_item, f, ensure_ascii=False, indent=4)


def update_drive_download_metadata(new_item: list, output_folder: str):
    """
    從 Google Drive 把檔案下載回來的時候，如果是新增的檔案，要更新 metadata
    """
    folder_id = output_folder.split("/")[-1]
    # if folder is not exist, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    file_path = os.path.join(
        output_folder, "{folder_id}-metadata.json".format(folder_id=folder_id)
    )
    with open(file_path, "r", encoding="utf-8") as file:
        dic_item = json.load(file)
    dic_item["items"].extend(new_item)
    # save dict as json, utf-8
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dic_item, f, ensure_ascii=False, indent=4)


def update_download_metadata_after_process_file(
    metadata_dir: str,
    lst_rag_metadata: List[RagMetadata],
):
    """
    每次做 txt split 的時候，會把一個檔案分成多個，這時候要更新 metadata
    @param metadata_dir: 資料夾路徑
    @param lst_rag_metadata: 分頁後的 metadata
    """
    from botrun_ask_folder.drive_download import append_export_extension_to_path
    from botrun_ask_folder.drive_download import truncate_filename

    # 2024-07-13 14:46 bowen to seba , drive_download_metadata.py
    # 發現這邊會有 exception 會讓整個程式碼跳出
    # 異常結束的情況之下會讓分頁程式碼只有分頁一頁就後面跑不完
    # 因此 bowen 加入了 try except 協助除錯完成
    try:
        dic_metadata = get_drive_download_metadata(metadata_dir)
        file_path = os.path.join(metadata_dir, get_metadata_file_name(metadata_dir))
        for rag_metadata in lst_rag_metadata:
            for item in dic_metadata["items"]:
                downloaded_file_name = truncate_filename(
                    append_export_extension_to_path(item["name"], item["mimeType"])
                )
                if (
                    downloaded_file_name == rag_metadata.ori_file_name
                    or downloaded_file_name
                    == rag_metadata.ori_file_name.rsplit(".", 1)[0]
                ):
                    new_item = item.copy()
                    new_item["name"] = rag_metadata.name
                    new_item["gen_page_imgs"] = rag_metadata.gen_page_imgs
                    new_item["ori_file_name"] = rag_metadata.ori_file_name
                    new_item["page_number"] = rag_metadata.page_number
                    if rag_metadata.sheet_name is not None:
                        new_item["sheet_name"] = rag_metadata.sheet_name
                    dic_metadata["items"].append(new_item)
                    break
        # save dict as json, utf-8
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dic_metadata, f, ensure_ascii=False, indent=4)
        current_folder_path = Path(__file__).resolve().absolute().parent
        parent_folder_path = current_folder_path.parent
        log_folder_path = parent_folder_path / "users" / "botrun_ask_folder"
        if not log_folder_path.exists():
            log_folder_path.mkdir(parents=True)
        shutil.copy2(file_path, log_folder_path / get_metadata_file_name(metadata_dir))
    except Exception as e:
        # import traceback
        # traceback.print_exc()
        print(f"drive_download_metadata.py, update_download_metadata, exception: {e}")


def get_drive_download_metadata(input_folder: str):
    metadata_path = os.path.join(input_folder, get_metadata_file_name(input_folder))
    if os.path.exists(metadata_path):
        # load json, utf-8
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_metadata_file_name(folder: str) -> str:
    folder_id = folder.split("/")[-1]
    return "{folder_id}-metadata.json".format(folder_id=folder_id)


async def init_drive_folder(folder_id: str, dic_result: dict):
    """
    Initialize a DriveFolder object and save it as a JSON file.
    Also, add all DriveFiles to Firestore.
    """
    # Create DriveFiles from dic_result['items']

    # Create DriveFolder
    drive_folder = DriveFolder(
        id=dic_result["parent_id"],
        status=DriveFolderStatus.PROCESSING,
        items=[item["id"] for item in dic_result["items"]],
        last_update_items_timestamp=datetime.now(pytz.timezone("Asia/Taipei")).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        last_update_items=[item["id"] for item in dic_result["items"]],
    )

    client = drive_client_factory()

    # Set the DriveFolder
    await client.set_drive_folder(drive_folder)

    print(f"Initialized DriveFolder to Firestore.")


async def set_drive_files(drive_files: list[DriveFile]):
    client = drive_client_factory()
    for drive_file in drive_files:
        await client.set_drive_file(drive_file)
        # await client.update_drive_file_status_in_folder(
        #     drive_file.folder_id, drive_file.id, drive_file.status
        # )

    print(f"Added {len(drive_files)} DriveFiles to Firestore.")


async def get_drive_files_need_update(drive_files: list[DriveFile]):
    """
    Get the drive files that need to be updated.
    """
    client = drive_client_factory()
    drive_files_need_update = []
    for drive_file in drive_files:
        ori_drive_file = await client.get_drive_file(drive_file.id)
        if ori_drive_file is None:
            drive_files_need_update.append(drive_file)
            continue
        if (
            ori_drive_file.status != DriveFileStatus.EMBEDDED
            or ori_drive_file.modifiedTime != drive_file.modifiedTime
        ):
            drive_files_need_update.append(drive_file)

    return drive_files_need_update


def update_new_items_to_drive_folder(folder_id: str, new_items: list):
    """
    Update the CollectionStatus with new items.

    Args:
        new_items (list): List of dictionaries containing new item data.
    """
    # Get the collection status client
    client = drive_client_factory()

    # Get the current collection status
    drive_folder = asyncio.run(client.get_drive_folder(folder_id))

    if drive_folder is None:
        print("Error: No existing Drive Folder found.")
        return

    # Convert new_items to CollectionItem objects
    new_drive_files = [DriveFile(**item) for item in new_items]

    # Save the updated collection status
    asyncio.run(client.set_drive_folder(drive_folder))
    # Update the collection status with new items
    asyncio.run(client.update_drive_files(drive_folder.id, new_drive_files))

    print(f"Updated CollectionStatus with {len(new_items)} new items.")


async def update_drive_file_after_process_file(
    drive_file: DriveFile,
    lst_rag_metadata: List[RagMetadata],
):
    """
    Update the CollectionStatus after processing files.

    Args:
        collection_id (str): The ID of the collection to update.
        lst_rag_metadata (List[RagMetadata]): List of processed file metadata.
    """

    # Get the collection status client
    client = drive_client_factory()

    # Get the current collection status
    # Update the collection items based on the processed files
    for rag_metadata in lst_rag_metadata:
        split_item = SplittedFile(
            id=str(uuid.uuid4()),  # Generate a new UUID for the SplittedFile
            name=rag_metadata.name,
            gen_page_imgs=rag_metadata.gen_page_imgs,
            ori_file_name=rag_metadata.ori_file_name,
            modified_time=drive_file.modifiedTime,
            page_number=(
                rag_metadata.page_number
                if rag_metadata.page_number != PAGE_NUMBER_NA
                else None
            ),
            sheet_name=(
                rag_metadata.sheet_name if rag_metadata.sheet_name is not None else None
            ),
            file_id=drive_file.id,  # Set the file_id to the parent DriveFile's id
            save_path=rag_metadata.save_path,
        )

        # Add the new SplitItem's id to the DriveFile's splitted_files list
        drive_file.splitted_files.append(split_item.id)

        # Save the SplittedFile
        await client.set_splitted_file(split_item)

    drive_file.status = DriveFileStatus.SPLITTED
    await client.set_drive_file(drive_file)
    # await client.update_drive_file_status_in_folder(
    #     drive_file.folder_id, drive_file.id, drive_file.status
    # )

    print(f"Updated drive file {drive_file.id} after processing file.")
