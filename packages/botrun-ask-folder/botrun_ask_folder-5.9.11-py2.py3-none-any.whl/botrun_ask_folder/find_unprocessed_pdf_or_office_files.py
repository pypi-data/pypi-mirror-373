import argparse
import os
from botrun_ask_folder.safe_join import safe_join


def has_txts_folder(path, file_name):
    base_name = os.path.splitext(file_name)[0]
    txts_path = safe_join(path, base_name + '.txts')
    # 檢查.txts目錄是否存在
    if os.path.exists(txts_path) and os.path.isdir(txts_path):
        # 檢查.txts目錄是否為空
        return os.listdir(txts_path) != []
    return False


def find_unprocessed_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.doc', '.docx', '.pdf')):
                if not has_txts_folder(root, file):
                    print(safe_join(root, file))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='找出沒有生成純文字的PDF或Office檔案')
    parser.add_argument('-d', '--directory', type=str, default='./data', help='要檢查的目錄路徑，預設為./data')
    args = parser.parse_args()

    find_unprocessed_files(args.directory)
