import asyncio
import aiohttp
import time
import os
from datetime import datetime
from typing import Dict, Any
import pytz
from urllib.parse import quote
from botrun_ask_folder.constants import MAX_CONCURRENT_PROCESS_FILES
from botrun_ask_folder.embeddings_to_qdrant import has_collection_in_qdrant
from botrun_ask_folder.translations import set_language, tr
from botrun_ask_folder.util.timestamp_encryp import (
    encrypt_timestamp,
    get_current_timestamp,
)
from .emoji_progress_bar import EmojiProgressBar
from .botrun_drive_manager import botrun_drive_manager
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

API_URL = os.getenv("BOTRUN_ASK_FOLDER_FAST_API_URL") + "/api/botrun/botrun_ask_folder"
API_TIMEOUT = 60
CHECK_INTERVAL = 20
BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN = os.getenv("BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN")
FOLDER_STATUS_ENC_KEY = os.getenv("FOLDER_STATUS_ENC_KEY")


async def process_folder_from_restapi(
    folder_id: str, force: bool = False, lang: str = "zh-TW"
):
    qdrant_host = os.getenv("QDRANT_HOST", "qdrant")
    qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
    qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
    qdrant_prefix = os.getenv("QDRANT_PREFIX", None)
    qdrant_https = os.getenv("QDRANT_HTTPS", "False").lower() == "true"
    collection_existed = await has_collection_in_qdrant(
        f"{folder_id}",
        qdrant_host,
        qdrant_port,
        qdrant_api_key,
        qdrant_prefix,
        qdrant_https,
    )
    headers = {"Authorization": f"Bearer {BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        # Start processing the folder
        process_url = f"{API_URL}/process-folder-job"
        data = {
            "folder_id": folder_id,
            "force": force,
            "embed": True,
            "qdrant_host": qdrant_host,
            "qdrant_port": qdrant_port,
            "qdrant_api_key": qdrant_api_key,
            "qdrant_prefix": qdrant_prefix,
            "qdrant_https": qdrant_https,
        }

        time1 = time.time()
        print(
            tr(
                "Start processing folder {folder_id} at {timestamp}",
                folder_id=folder_id,
                timestamp=get_timestamp(),
            )
        )
        async with session.post(
            process_url, json=data, headers=headers, timeout=API_TIMEOUT
        ) as response:
            initial_response = await response.json()
            if initial_response.get("status") == "success":
                print(
                    tr(
                        "List all files in {folder_id}, job_id: {job_id} {timestamp}",
                        folder_id=folder_id,
                        job_id=initial_response.get("job_id"),
                        timestamp=get_timestamp(),
                    )
                )
            else:
                print(
                    tr(
                        "Data {folder_id} import job failed: {message} at {timestamp}",
                        folder_id=folder_id,
                        message=initial_response.get("message"),
                        timestamp=get_timestamp(),
                    )
                )
                return

        # Initialize EmojiProgressBar
        # progress_bar = EmojiProgressBar(total=1)  # Initialize with 1, will update later
        # progress_bar.set_description(
        #     f"{folder_id} 資料匯入中，檢查狀態更新時間：{get_timestamp()}"
        # )

        # Check status periodically
        status_url = f"{API_URL}/folder-status"
        action_started_at_datetime = datetime.now(pytz.timezone("Asia/Taipei"))
        action_started_at = action_started_at_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # URL encode the parameters
        encoded_folder_id = quote(folder_id)

        enc_data = encrypt_timestamp(action_started_at_datetime)

        if lang == "en":
            check_url = f"{API_URL}/folder_status_web_en?folder_id={encoded_folder_id}&enc_data={enc_data}&action_started_at={action_started_at}"
        else:
            check_url = f"{API_URL}/folder_status_web?folder_id={encoded_folder_id}&enc_data={enc_data}&action_started_at={action_started_at}"

        print(
            tr(
                "Please click this link to check the import status: {check_url}",
                check_url=check_url,
            )
        )
        while True:
            await asyncio.sleep(CHECK_INTERVAL)

            try:
                async with session.post(
                    status_url,
                    json={
                        "folder_id": folder_id,
                        "action_started_at": action_started_at,
                    },
                    headers=headers,
                    timeout=API_TIMEOUT,
                ) as response:
                    status = await response.json()
                if status.get("status") == "WAITING":
                    # print(f"{folder_id} 初始化中，檢查狀態更新時間：{get_timestamp()}")
                    continue
                total_files = status.get("total_files", 0)
                # embedded_files = status.get("embedded_files", 0)

                if total_files > 0 and status.get("status") != "DONE":
                    # print(
                    #     f"{folder_id} 資料匯入中，檢查狀態更新時間：{get_timestamp()}"
                    # )
                    pass

                if status.get("status") == "DONE":
                    print(
                        tr(
                            "{folder_id} data import completed, can start using {timestamp}",
                            folder_id=folder_id,
                            timestamp=get_timestamp(),
                        )
                    )
                    time2 = time.time()
                    total_seconds = int(time2 - time1)
                    minutes, seconds = divmod(total_seconds, 60)
                    time_str = f"{minutes:02d}:{seconds:02d}"
                    print(
                        tr(
                            "Data import completed, took {time_str}, processed {total_files} files",
                            time_str=time_str,
                            total_files=total_files,
                        )
                    )
                    botrun_file_name = (
                        f"波{folder_id}" if lang == "zh-TW" else f"Bot{folder_id}"
                    )
                    if not collection_existed:
                        botrun_drive_manager(
                            botrun_file_name, f"{folder_id}", force=force, lang=lang
                        )
                    elif force:
                        botrun_drive_manager(
                            botrun_file_name, f"{folder_id}", force=force, lang=lang
                        )
                    return
                elif status.get("status") == "FAILED":
                    print(
                        tr(
                            "{folder_id} data import failed, please contact our customer service partners!",
                            folder_id=folder_id,
                        )
                    )
                    return

            except asyncio.TimeoutError:
                print(
                    tr(
                        "Check import job {folder_id} timeout at {timestamp}",
                        folder_id=folder_id,
                        timestamp=get_timestamp(),
                    )
                )
            except Exception as e:
                print(
                    tr(
                        "Check import job {folder_id} failed: {message} at {timestamp}",
                        folder_id=folder_id,
                        message=str(e),
                        timestamp=get_timestamp(),
                    )
                )


def process_folder(
    folder_id: str, force: bool = False, lang: str = "zh-TW"
) -> Dict[str, Any]:
    set_language(lang)
    return asyncio.run(process_folder_from_restapi(folder_id, force, lang))


def get_timestamp():
    return datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S")
