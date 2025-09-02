import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Optional
import pytz
from botrun_ask_folder.drive_download import (
    drive_download_with_service,
    file_download_with_service,
)
from botrun_ask_folder.drive_download_metadata import (
    get_drive_files_need_update,
    init_drive_folder,
    set_drive_files,
)
from botrun_ask_folder.drive_list_files import drive_list_files_with_service
from botrun_ask_folder.google_drive_service import get_google_drive_service
from botrun_ask_folder.embeddings_to_qdrant import (
    has_collection_in_qdrant,
    init_qdrant_collection,
)
from botrun_ask_folder.models.drive_file import DriveFile, DriveFileStatus
from botrun_ask_folder.models.drive_folder import DriveFolderStatus
from botrun_ask_folder.models.job_event import JobEvent, JobStatus, JobType
from botrun_ask_folder.models.splitted_file import SplittedFileStatus
from botrun_ask_folder.run_split_txts import run_split_txts_for_distributed
from botrun_ask_folder.embeddings_to_qdrant import embeddings_to_qdrant_distributed
from botrun_ask_folder.services.drive.drive_factory import drive_client_factory
from dotenv import load_dotenv
from botrun_ask_folder.constants import MAX_CONCURRENT_PROCESS_FILES, MAX_WORKERS
from google.cloud import run_v2
from google.oauth2 import service_account
import random
import time

from botrun_ask_folder.services.queue.queue_factory import queue_client_factory

load_dotenv()


# 定義一個自定義的 log formatter
class TaipeiTimeFormatter(logging.Formatter):
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        taipei_tz = pytz.timezone("Asia/Taipei")
        return taipei_tz.localize(dt)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat(timespec="milliseconds")


# 設置 logging
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = TaipeiTimeFormatter(
        "%(asctime)s - %(filename)s:%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# 使用設置的 logger
logger = setup_logger()


async def process_job():
    logger.info("Processing job")
    queue_client = queue_client_factory()
    pending_count = await queue_client.get_pending_job_count()
    logger.info(f"Pending job count: {pending_count}")
    job_event = await queue_client.dequeue()
    if job_event is None:
        logger.info("No job event found")
        return
    data = json.loads(job_event.data)
    logger.info(f"json loads job_event.data: {data}")
    try:
        if job_event.job_type == JobType.LIST_FILES.value:
            await process_folder_job(
                folder_id=data["folder_id"],
                force=data["force"],
                embed=True,
                qdrant_host=data["qdrant_host"],
                qdrant_port=data["qdrant_port"],
                qdrant_api_key=data["qdrant_api_key"],
                qdrant_prefix=data["qdrant_prefix"],
                qdrant_https=data["qdrant_https"],
            )
        elif job_event.job_type == JobType.HANDLE_FILES.value:
            await process_file_ids(
                folder_id=data["folder_id"],
                file_ids=data["file_ids"],
                force=data["force"],
                embed=True,
                qdrant_host=data["qdrant_host"],
                qdrant_port=data["qdrant_port"],
                qdrant_api_key=data["qdrant_api_key"],
                qdrant_prefix=data["qdrant_prefix"],
                qdrant_https=data["qdrant_https"],
            )
        await queue_client.complete_job(job_event.id)
    except Exception as e:
        import traceback

        traceback.print_exc()
        try:
            await queue_client.fail_job(job_event.id, str(e))
        except Exception as e2:
            logger.error(f"error in fail_job: {str(e2)}")
        logger.error(f"Error in process_job: {str(e)} job_id: {job_event.id}")
        raise e


async def process_folder_job(
    folder_id: str,
    force: bool,
    embed: bool,
    qdrant_host: str,
    qdrant_port: int,
    qdrant_api_key: str,
    qdrant_prefix: Optional[str] = None,
    qdrant_https: bool = False,
):
    logger.info(
        f"Cloud run job Processing folder {folder_id} with force={force} and embed={embed}"
    )
    logger.info(f"Qdrant settings: host={qdrant_host}, port={qdrant_port}")
    logger.info(f"fast_api: {os.getenv('BOTRUN_ASK_FOLDER_FAST_API_URL')}")
    collection_existed = await has_collection_in_qdrant(
        folder_id,
        qdrant_host,
        qdrant_port,
        qdrant_api_key,
        qdrant_prefix,
        qdrant_https,
    )
    logger.info(f"collection_existed: {collection_existed}")

    drive_client = drive_client_factory()
    if force:
        logger.info(f"Deleting folder {folder_id} because force is true")
        await drive_client.delete_drive_folder(folder_id)
    drive_folder = await drive_client.get_drive_folder(folder_id)
    if drive_folder is not None and collection_existed:
        drive_folder.status = DriveFolderStatus.PROCESSING
        await drive_client.set_drive_folder(drive_folder)

    service = get_google_drive_service()

    try:
        logger.info(f"Initializing qdrant collection for folder {folder_id}")
        await init_qdrant_collection(
            folder_id,
            force=force,
            qdrant_host=qdrant_host,
            qdrant_port=qdrant_port,
            qdrant_api_key=qdrant_api_key,
            qdrant_prefix=qdrant_prefix,
            qdrant_https=qdrant_https,
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        logger.error(
            f"init_qdrant_collection folder_id {folder_id} 失敗，錯誤訊息：{e}"
        )
        raise e

    dic_result = drive_list_files_with_service(service, folder_id, max_files=9999999)
    logger.info(f"Listed from {folder_id}, result: {dic_result}")

    drive_files = [
        DriveFile(
            id=item["id"],
            name=item["name"],
            modifiedTime=item["modifiedTime"],
            mimeType=item["mimeType"],
            size=item.get("size", ""),
            parent=item.get("parent", ""),
            path=item.get("path", ""),
            folder_id=folder_id,
        )
        for item in dic_result["items"]
    ]
    drive_files_need_update = drive_files
    if drive_folder is None:
        await init_drive_folder(folder_id, dic_result)
        await set_drive_files(drive_files)
        # 确保 init_drive_folder 完成后再继续
        logger.info(
            f"Initialized drive folder {folder_id}, prepare to download all files from folder (drive_folder is None)"
        )
    elif drive_folder is not None and not collection_existed:
        await init_drive_folder(folder_id, dic_result)
        await set_drive_files(drive_files)
        logger.info(
            f"Initialized drive folder {folder_id}, prepare to download all files from folder (collection_existed is False)"
        )
    else:
        # 表示是更新
        drive_files_need_update = await get_drive_files_need_update(drive_files)
        logger.info(
            f"Folder {folder_id} drive_files_need_update: {drive_files_need_update}"
        )
        await set_drive_files(drive_files_need_update)
        drive_folder.last_update_items = [item.id for item in drive_files_need_update]
        drive_folder.last_update_items_timestamp = datetime.now(
            pytz.timezone("Asia/Taipei")
        ).strftime("%Y-%m-%d %H:%M:%S")
        drive_folder.last_update_failed_items = []
        drive_folder.items = drive_folder.items + [
            item.id for item in drive_files_need_update
        ]
        drive_folder.items = list(set(drive_folder.items))
        await drive_client.set_drive_folder(drive_folder)
    # items = dic_result["items"]

    # 将文件 ID 分组
    file_id_groups = [
        drive_files_need_update[i : i + MAX_CONCURRENT_PROCESS_FILES]
        for i in range(0, len(drive_files_need_update), MAX_CONCURRENT_PROCESS_FILES)
    ]
    if len(file_id_groups) == 0 and drive_folder is not None:
        drive_folder.status = DriveFolderStatus.DONE
        logger.info(
            f"Folder {folder_id} status set to done because no files need to update"
        )
        await drive_client.set_drive_folder(drive_folder)

    # 为每组文件触发一个 Cloud Run Job
    queue_client = queue_client_factory()
    for group in file_id_groups:
        file_ids = ",".join([drive_file.id for drive_file in group])
        await queue_client.enqueue(
            JobEvent(
                job_type=JobType.HANDLE_FILES,
                status=JobStatus.PENDING,
                data=json.dumps(
                    {
                        "folder_id": folder_id,
                        "force": force,
                        "file_ids": file_ids,
                        "qdrant_host": qdrant_host,
                        "qdrant_port": qdrant_port,
                        "qdrant_api_key": qdrant_api_key,
                        "qdrant_prefix": qdrant_prefix,
                        "qdrant_https": qdrant_https,
                    },
                ),
            )
        )

        # trigger_cloud_run_job(
        #     folder_id, force, embed, file_ids, qdrant_host, qdrant_port, qdrant_api_key
        # )
    pending_count = await queue_client.get_pending_job_count()
    logger.info(f"Pending job count: {pending_count}")
    if pending_count > MAX_WORKERS:
        for _ in range(MAX_WORKERS):
            trigger_cloud_run_job()
    elif pending_count > 0:
        for _ in range(pending_count):
            trigger_cloud_run_job()

    # logger.info(f"Total triggered jobs for folder {folder_id}: {job_count}")


def trigger_cloud_run_job():
    google_service_account_key_path = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS_FOR_FASTAPI",
        "/app/keys/scoop-386004-d22d99a7afd9.json",
    )
    credentials = service_account.Credentials.from_service_account_file(
        google_service_account_key_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    client = run_v2.JobsClient(credentials=credentials)
    project = credentials.project_id
    job_name = f"projects/{project}/locations/{os.getenv('CLOUD_RUN_REGION', 'asia-east1')}/jobs/process-folder-job"

    container_override = run_v2.RunJobRequest.Overrides.ContainerOverride(
        name="asia-east1-docker.pkg.dev/scoop-386004/botrun-ask-folder/botrun-ask-folder-job",
    )

    job_overrides = run_v2.RunJobRequest.Overrides(
        container_overrides=[container_override]
    )
    request = run_v2.RunJobRequest(name=job_name, overrides=job_overrides)

    try:
        operation = client.run_job(request=request)
    except Exception as e:
        import traceback

        traceback.print_exc()
        logger.error(f"Error in trigger_cloud_run_job: {str(e)}")
        # 做失敗讓它結束，不然會一直retry
        return
    logger.info(f"Triggered Cloud Run Job {operation.metadata.name}")


async def process_file_ids(
    folder_id: str,
    file_ids: str,
    force: bool,
    embed: bool,
    qdrant_host: str,
    qdrant_port: int,
    qdrant_api_key: str,
    qdrant_prefix: Optional[str] = None,
    qdrant_https: bool = False,
):
    service = get_google_drive_service()
    file_id_list = file_ids.split(",")
    for index, file_id in enumerate(file_id_list):
        drive_client = drive_client_factory()
        drive_file = await drive_client.get_drive_file(file_id)
        is_last_file = index == len(file_id_list) - 1
        try:
            await download_single_file_and_embed(
                drive_file,
                service,
                force,
                embed,
                qdrant_host,
                qdrant_port,
                qdrant_api_key,
                is_last_file=is_last_file,
                qdrant_prefix=qdrant_prefix,
                qdrant_https=qdrant_https,
            )
        except Exception as e:
            try:
                drive_folder = await drive_client.get_drive_folder(folder_id)
                drive_folder.last_update_failed_items.append(drive_file.id)
                drive_folder.status = DriveFolderStatus.FAILED
                await drive_client.set_drive_folder(drive_folder)
            except Exception as e2:
                logger.error(f"Error in update drive folder status failed: {str(e2)}")
    queue_client = queue_client_factory()
    pending_count = await queue_client.get_pending_job_count()
    logger.info(f"Pending job count: {pending_count}")
    if pending_count > MAX_WORKERS:
        for _ in range(MAX_WORKERS):
            trigger_cloud_run_job()
    elif pending_count > 0:
        for _ in range(pending_count):
            trigger_cloud_run_job()


async def download_single_file_and_embed(
    drive_file: DriveFile,
    service,
    force: bool,
    embed: bool,
    qdrant_host: str,
    qdrant_port: int,
    qdrant_api_key: str,
    is_last_file: bool = False,
    qdrant_prefix: Optional[str] = None,
    qdrant_https: bool = False,
):
    retry_count = 3
    while retry_count > 0:
        try:
            folder_path = "./data"
            logger.info(
                f"Downloading file: {drive_file.id} is_last_file: {is_last_file}"
            )
            drive_file = file_download_with_service(
                service, drive_file, folder_path, force=force
            )

            if force:
                drive_file.splitted_files = []

            drive_client = drive_client_factory()
            await drive_client.set_drive_file(drive_file)

            await run_split_txts_for_distributed(drive_file, force=force)
            logger.info(f"File: {drive_file.id} splitted")

            await embed_file(
                drive_file,
                qdrant_host,
                qdrant_port,
                qdrant_api_key,
                is_last_file,
                qdrant_prefix=qdrant_prefix,
                qdrant_https=qdrant_https,
            )
            break
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(f"Error in download_single_file_and_embed: {str(e)}")
            retry_count -= 1
            if retry_count == 0:
                logger.error(f"Retry count is 0, file {drive_file.id} failed")
                raise e


async def embed_file(
    drive_file: DriveFile,
    qdrant_host: str,
    qdrant_port: int,
    qdrant_api_key: str,
    is_last_file: bool,
    qdrant_prefix: Optional[str] = None,
    qdrant_https: bool = False,
):
    embed_success = False
    try:
        logger.info(f"_handle_download_and_embed Embedding file: {drive_file.id}")
        embed_success = await embeddings_to_qdrant_distributed(
            drive_file,
            qdrant_host=qdrant_host,
            qdrant_port=qdrant_port,
            qdrant_api_key=qdrant_api_key,
            qdrant_prefix=qdrant_prefix,
            qdrant_https=qdrant_https,
        )
        logger.info(
            f"_handle_download_and_embed Embedding file: {drive_file.id} done, check success: {embed_success}"
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        logger.error(f"Embedding 失敗，錯誤訊息：{e} for file {drive_file.id}")

    if embed_success:
        drive_file.status = DriveFileStatus.EMBEDDED
        drive_client = drive_client_factory()
        await drive_client.set_drive_file(drive_file)
        logger.info(
            f"Folder {drive_file.folder_id} Embedding file: {drive_file.id} set status to embedded"
        )
        # await drive_client.update_drive_file_status_in_folder(
        #     drive_file.folder_id, drive_file.id, drive_file.status
        # )
        await finalize_embed(drive_file, is_last_file)


async def mark_file_as_embedded(drive_file: DriveFile, is_last_file: bool):
    drive_client = drive_client_factory()
    for split_id in drive_file.splitted_files:
        split_file = await drive_client.get_splitted_file(split_id)
        split_file.status = SplittedFileStatus.EMBEDDED
        await drive_client.set_splitted_file(split_file)
    drive_file.status = DriveFileStatus.EMBEDDED
    await drive_client.set_drive_file(drive_file)
    # await drive_client.update_drive_file_status_in_folder(
    #     drive_file.folder_id, drive_file.id, drive_file.status
    # )
    await finalize_embed(drive_file, is_last_file)


async def finalize_embed(drive_file: DriveFile, is_last_file: bool = False):
    """
    @param is_last_file: 因為有可能發生檔案太多的情況，所以 finalize_embed 在這批的最後一個檔案才要做
    """

    logger.info(f"_finalize_embed called from {drive_file.id}")
    drive_client = drive_client_factory()

    # Clean up split files
    for item in drive_file.splitted_files:
        split_file = await drive_client.get_splitted_file(item)
        split_file.status = SplittedFileStatus.EMBEDDED
        await drive_client.set_splitted_file(split_file)
        if split_file.save_path:
            try:
                logger.info(
                    f"Removing split file {split_file.id} save path, from file {drive_file.id}"
                )
                os.remove(split_file.save_path)
            except Exception as e:
                logger.error(
                    f"Error removing split file {split_file.id} save path: {e}"
                )

    # Clean up drive file
    if drive_file.save_path:
        try:
            logger.info(f"Removing drive file {drive_file.id} save path")
            os.remove(drive_file.save_path)
        except Exception as e:
            logger.info(f"Error removing drive file {drive_file.id} save path: {e}")

    # Check folder status only for the last file
    if is_last_file:
        await check_folder_status(drive_file.folder_id)

    logger.info(
        f"Finalize embed for drive file {drive_file.id} is_last_file: {is_last_file}"
    )


async def check_folder_status(folder_id: str):
    drive_client = drive_client_factory()
    drive_folder = await drive_client.get_drive_folder(folder_id)

    if drive_folder is None:
        logger.error(f"Drive folder {folder_id} not found")
        return

    non_embedded_files_count = await drive_client.get_non_embedded_files_count(
        drive_folder.items
    )

    if non_embedded_files_count == 0:
        drive_folder.status = DriveFolderStatus.DONE
        logger.info(f"All files embedded, updating folder {folder_id} status to done")
        await drive_client.set_drive_folder(drive_folder)
    else:
        logger.info(
            f"Folder {folder_id} has {non_embedded_files_count} non-embedded files"
        )
