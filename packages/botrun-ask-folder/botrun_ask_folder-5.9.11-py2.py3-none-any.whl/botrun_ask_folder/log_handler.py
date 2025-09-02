# log_handler.py
import os
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9 以上版本使用


class LogHandler:
    def __init__(self, base_dir="./logs", file_prefix="split_txts.py"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        # 使用 file_prefix 參數來自訂日誌檔案的前綴名稱
        self.log_file_path = os.path.join(
            self.base_dir, f"{datetime.now().strftime('%Y-%m-%d')}_{file_prefix}.log"
        )

    def write_log(self, message):
        # 獲取當前時區的時間
        current_time = datetime.now(ZoneInfo("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{current_time}] {message}"
        with open(self.log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(log_message + "\n")
