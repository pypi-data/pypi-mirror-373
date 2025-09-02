import csv
import requests
import time
import json
from datetime import datetime, timedelta
import pytz
import os
import sys
import time
from dotenv import load_dotenv
from urllib.parse import quote
import aiohttp
import asyncio
from botrun_ask_folder.util.timestamp_encryp import (
    encrypt_timestamp,
    get_current_timestamp,
)
import ssl
import shutil

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 創建一個不驗證證書的 SSL 上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

load_dotenv()

UPDATE_SETTING_CSV_URL = os.getenv("UPDATE_SETTING_CSV_URL","")
JSON_PATH = os.getenv("JSON_PATH","logs/last_update.json")
BOTRUN_ASK_FOLDER_FAST_API_URL = os.getenv("BOTRUN_ASK_FOLDER_FAST_API_URL","")
BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN= os.getenv("BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN", "")
QDRANT_HOST = os.getenv("QDRANT_HOST", "")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", 60))


async def update_folder(drive_folder_id):
    is_update_success=False
    print(f"Updating folder: {drive_folder_id}")
    # 在這裡實現實際的資料夾更新邏輯
    API_URL = BOTRUN_ASK_FOLDER_FAST_API_URL + "/api/botrun/botrun_ask_folder"
    headers={"Authorization": f"Bearer {BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN}"} 
    qdrant_host=QDRANT_HOST
    qdrant_port=QDRANT_PORT
    qdrant_api_key=QDRANT_API_KEY    


    # Start processing the folder
    process_url = f"{API_URL}/process-folder-job"
    action_started_at_datetime = datetime.now(pytz.timezone("Asia/Taipei"))
    action_started_at = action_started_at_datetime.strftime("%Y-%m-%d %H:%M:%S")

    print(f" 開始執行資料 {drive_folder_id} 匯入工作, action_started_at={action_started_at}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                process_url,
                json={
                    "folder_id": drive_folder_id,
                    "force": False,
                    "embed": True,
                    "qdrant_host": qdrant_host,
                    "qdrant_port": qdrant_port,
                    "qdrant_api_key": qdrant_api_key,
                },
                headers=headers,
                timeout=API_TIMEOUT,
                ssl=ssl_context
            ) as response:
                initial_response = await response.json()
                if initial_response.get("status") == "success":
                    print(
                        f" 成功！ 更新知識庫工作成功！條列所有 {drive_folder_id} 的檔案, job_id: {initial_response.get('job_id')}"
                    )
                    is_update_success = True
                else:
                    print(
                        f" 失敗.. 資料 {drive_folder_id} 更新知識庫工作失敗: 得到訊息 {initial_response}"
                    )
                    is_update_success = False
        except asyncio.TimeoutError:
            print(f"[update_files_from_drive.py] 更新知識庫工作 {drive_folder_id} 逾時...")
            is_update_success = False
        except Exception as e:
            print(f"[update_files_from_drive.py] 更新知識庫工作 {drive_folder_id} 失敗: {str(e)}")
            is_update_success = False

    print(f"[update_files_from_drive.py] update_folder() : {drive_folder_id} 程式結尾。is_update_success={is_update_success}")
    return is_update_success


async def check_is_running(drive_folder_id):
    is_running=False

    API_URL = BOTRUN_ASK_FOLDER_FAST_API_URL + "/api/botrun/botrun_ask_folder"
    headers={"Authorization": f"Bearer {BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN}"} 
    qdrant_host=QDRANT_HOST
    qdrant_port=QDRANT_PORT
    qdrant_api_key=QDRANT_API_KEY    

    # Check status periodically
    status_url = f"{API_URL}/folder-status"
    action_started_at_datetime = datetime.now(pytz.timezone("Asia/Taipei"))
    action_started_at = action_started_at_datetime.strftime("%Y-%m-%d %H:%M:%S")

    print(f" ------action_started_at={action_started_at}")

    async with aiohttp.ClientSession() as session:
        #await asyncio.sleep(CHECK_INTERVAL)

        try:
            async with session.post(
                status_url,
                json={
                    "folder_id": drive_folder_id
                },
                headers=headers,
                timeout=API_TIMEOUT,
                ssl=ssl_context
            ) as response:
                status = await response.json()
            if status.get("status") == "WAITING":
                is_running=False
                print(f"[update_files_from_drive.py] check_is_running() : {drive_folder_id} 依然在初始化中或是還沒開始跑。is_running={is_running}")
                return is_running 

            total_files = status.get("total_files", 0)
            # embedded_files = status.get("embedded_files", 0)

            if total_files > 0 and status.get("status") != "DONE":
                is_running=True
                print(f"[update_files_from_drive.py] check_is_running() : {drive_folder_id} 資料匯入中。is_running={is_running}")
                return is_running 

            if status.get("status") == "DONE":
                is_running=False
                print(f"[update_files_from_drive.py] check_is_running() : {drive_folder_id} 資料匯入完成，可以開始使用，共處理 {total_files} 個檔案。is_running={is_running}")
                return is_running 

        except asyncio.TimeoutError:
            print(f"檢查匯入工作 {drive_folder_id} 逾時...")
        except Exception as e:
            print(f"檢查匯入工作 {drive_folder_id} 失敗: {str(e)}")

    print(f"[update_files_from_drive.py] check_is_running() : {drive_folder_id} 程式結尾。is_running={is_running}")
    return is_running

def read_csv_from_url(url):
    response = requests.get(url)
    content = response.content.decode('utf-8')
    csv_data = list(csv.reader(content.splitlines()))
    return csv_data[2:]  # 跳過前兩行

def load_last_update_data():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_last_update_data(data):
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def update_json_data(folders):
    last_update_data = load_last_update_data()
    current_folder_ids = set()

    for folder in folders:
        _, _, bot_name, drive_folder_id, update_duration, _ = folder[:6]
        current_folder_ids.add(drive_folder_id)

        if drive_folder_id not in last_update_data:
            last_update_data[drive_folder_id] = {
                "bot_name": bot_name,
                "update_duration": int(update_duration),
                "last_update": datetime.min.isoformat()
            }
        else:
            last_update_data[drive_folder_id].update({
                "bot_name": bot_name,
                "update_duration": int(update_duration)
            })

    # Remove folders that are not in the current CSV
    for folder_id in list(last_update_data.keys()):
        if folder_id not in current_folder_ids:
            del last_update_data[folder_id]

    save_last_update_data(last_update_data)
    return last_update_data

def check_env_variables():
    required_vars = [
        "UPDATE_SETTING_CSV_URL",
        "JSON_PATH",
        "BOTRUN_ASK_FOLDER_FAST_API_URL",
        "BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN",
        "QDRANT_HOST",
        "QDRANT_PORT",
        "QDRANT_API_KEY",
        "API_TIMEOUT"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.strip() == "":
            missing_vars.append(var)
    
    if missing_vars:
        print(f"錯誤: 以下環境變數未設置或為空字串: {', '.join(missing_vars)}")
        sys.exit(1)

    print(f"[update_files_from_drive.py] check_env_variables success, 資料正確載入")



def update_files_from_drive():
    csv_url = UPDATE_SETTING_CSV_URL

    #進行檢查並更新    
    folders = read_csv_from_url(csv_url)
    print(folders)
    last_update_data = update_json_data(folders)

    now = datetime.now()

    for folder in folders:
        _, domain, bot_name, drive_folder_id, _, _ = folder[:6]
        folder_data = last_update_data[drive_folder_id]
        last_update = datetime.fromisoformat(folder_data["last_update"])
        update_duration = folder_data["update_duration"]

        next_update = last_update + timedelta(hours=update_duration)

        if now >= next_update:
            if asyncio.run(check_is_running(drive_folder_id)):
                print(f"[update_files_from_drive.py] (Skipped): {bot_name} ({domain}) is already running. Will try again next round.")
                continue

            print(f"[update_files_from_drive.py] (Updating): {bot_name} ({domain})...")
            try:
                folder_data["is_running"] = True
                save_last_update_data(last_update_data)  # 保存狀態變更
                
                is_update_success = True
                is_update_success = asyncio.run(update_folder(drive_folder_id))

                if is_update_success:                
                    folder_data["last_update"] = now.isoformat()
                    folder_data["is_running"] = True
                    print(f"[update_files_from_drive.py] Successfully send update for {bot_name}")
                else: 
                    folder_data["is_running"] = False
                    print(f"[update_files_from_drive.py] Failed to update {bot_name}")
            except Exception as e:
                folder_data["is_running"] = False
                print(f"[update_files_from_drive.py] Failed to update {bot_name}: {str(e)}")
            finally:
                save_last_update_data(last_update_data)  # 無論成功與否，都保存狀態
        else:
            time_left = next_update - now
            print(f"[update_files_from_drive.py] (Pending): {bot_name} next update in {time_left}")

    print("[update_files_from_drive.py] All updates checked. Last update data saved.")



### <process_get_folder_status>
## 這一段是定時檢查每個波通鑑更新狀況，並將結果存到 json 檔案中
## 排程要放在 update_files_from_drive() 之後
async def get_folder_status(drive_folder_id):
    API_URL = BOTRUN_ASK_FOLDER_FAST_API_URL + "/api/botrun/botrun_ask_folder"
    headers = {"Authorization": f"Bearer {BOTRUN_ASK_FOLDER_JWT_STATIC_TOKEN}"}
    status_url = f"{API_URL}/folder-status"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                status_url,
                json={
                    "folder_id": drive_folder_id,
                    "include_file_status": False
                },
                headers=headers,
                timeout=API_TIMEOUT,
                ssl=ssl_context
            ) as response:
                status = await response.json()
                return status
        except Exception as e:
            print(f"Error getting status for folder {drive_folder_id}: {str(e)}")
            return None

def save_folder_status(drive_folder_id, status):
    os.makedirs("logs/folder_id", exist_ok=True)
    file_path = f"logs/folder_id/{drive_folder_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    print(f"Status saved to {file_path}")

async def process_get_folder_status():
    csv_url = UPDATE_SETTING_CSV_URL
    folders = read_csv_from_url(csv_url)
    
    for folder in folders:
        _, _, bot_name, drive_folder_id, _, _ = folder[:6]
        print(f"Getting status for {bot_name} (Folder ID: {drive_folder_id})...")
        status = await get_folder_status(drive_folder_id)
        if status:
            save_folder_status(drive_folder_id, status)

    check_and_cp_static_html_files()
###</process_get_folder_status>


###<check_and_cp_static_html_files>
def check_and_cp_static_html_files():
    html_files = ['botdoc_status_check.html'] #['__filename_decoder.html', 'botdoc_status_check.html']
    # __filename_decoder.html 可以產生讀取狀態檔案 "last_update.json" 編碼後的文字，避免路徑在純前端網頁 botdoc_status_check.html 被察覺
    logs_dir = 'logs'
    static_dir = 'static'

    # 確保logs目錄存在
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    for html_file in html_files:
        logs_file_path = os.path.join(logs_dir, html_file)
        static_file_path = os.path.join(static_dir, html_file)

        if not os.path.exists(logs_file_path):
            if os.path.exists(static_file_path):
                try:
                    shutil.copy2(static_file_path, logs_file_path)
                    print(f"已成功複製 {html_file} 到 logs 目錄")
                except Exception as e:
                    print(f"複製 {html_file} 時發生錯誤: {str(e)}")
            else:
                print(f"錯誤: 在 static 目錄中找不到 {html_file}")
        else:
            print(f"檢查通過: {html_file} 已存在於 logs 目錄")
###</check_and_cp_static_html_files>


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "get-folder-status":
            print(f"[update_files_from_drive.py] processing 01 get-folder-status...")
            asyncio.run(process_get_folder_status())
            return
        if sys.argv[1] == "update-files-from-drive":
            print(f"[update_files_from_drive.py] processing 02 update-files-from-drive......")
            update_files_from_drive()
            return
        elif sys.argv[1] != "update-files-from-drive":
            print("Invalid argument. Use 'python update_files_from_drive.py update-files-from-drive' or 'python update_files_from_drive.py get-folder-status'.")
            return

    # 預設給參數，跑更新
    print(f"[update_files_from_drive.py] processing update-files-from-drive......")
    update_files_from_drive()



if __name__ == "__main__":

    print(f"[update_files_from_drive.py] =====================")
    print(f"[update_files_from_drive.py] update list file={JSON_PATH}")

    check_env_variables()
    main()

    print(f"[update_files_from_drive.py] update finished")
    print(f"[update_files_from_drive.py] =====================")

