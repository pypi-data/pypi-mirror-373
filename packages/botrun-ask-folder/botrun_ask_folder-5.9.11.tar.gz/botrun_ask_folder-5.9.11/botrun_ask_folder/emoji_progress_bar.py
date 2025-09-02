# emoji_progress_bar.py
import argparse
import sys

import time
from datetime import datetime, timedelta


class EmojiProgressBar:
    def __init__(self, total):
        self.total = total
        self.start_time = datetime.now()
        self.last_print_time = self.start_time
        self.first_update = True
        self.description = ""

    def _format_time(self, seconds):
        return str(timedelta(seconds=seconds)).split(".")[0]

    def update(self, progress):
        current_time = datetime.now()
        elapsed_time = current_time - self.start_time
        elapsed_seconds = elapsed_time.total_seconds()
        percent = (progress / self.total) * 100
        estimated_total_time = elapsed_seconds / progress * self.total
        remaining_time = max(0, estimated_total_time - elapsed_seconds)

        # 檢查是否為第一次更新或進度條更新間隔超過10秒，或進度已達100%
        if self.first_update or (current_time - self.last_print_time).total_seconds() > 10 or progress == self.total:
            if self.description == "":
                print(
                    f"🔄{percent:.0f}% ({progress}/{self.total}) "
                    f"🕒{self._format_time(elapsed_seconds)} "
                    f"⏳{self._format_time(remaining_time)}                    ", flush=True)
            else:
                print(
                    f"🔄{percent:.0f}% ({progress}/{self.total}) "
                    f"🕒{self._format_time(elapsed_seconds)} "
                    f"⏳{self._format_time(remaining_time)} "
                    f"📝{self.description}                    ", flush=True)
            sys.stdout.flush()

            self.last_print_time = current_time
            self.first_update = False

    def set_description(self, description):
        self.description = description


def emoji_progress_bar(progress_bar, total, step, update_interval):
    progress = 0
    while progress < total:
        progress += step
        progress = min(progress, total)
        progress_bar.update(progress)
        time.sleep(update_interval)


def main():
    parser = argparse.ArgumentParser(description="進度條示範")
    parser.add_argument("--total", type=int, default=3000, help="任務的總數量")
    parser.add_argument("--update_interval", type=float, default=0.2, help="進度更新之間的間隔時間（秒）")
    parser.add_argument("--step", type=int, default=15, help="每次進度增加的單位")
    args = parser.parse_args()

    progress_bar = EmojiProgressBar(args.total)
    emoji_progress_bar(progress_bar, args.total, args.step, args.update_interval)


if __name__ == "__main__":
    main()
