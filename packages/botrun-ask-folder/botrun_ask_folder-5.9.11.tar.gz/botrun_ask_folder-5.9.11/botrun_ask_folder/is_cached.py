# is_cached.py
import os


def is_cached(folder_or_file_path: str, force: bool) -> bool:
    if force:
        return False
    if os.path.isdir(folder_or_file_path):
        return len(os.listdir(folder_or_file_path)) > 0
    elif os.path.isfile(folder_or_file_path):
        return os.path.exists(folder_or_file_path)
    else:
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check if a folder or file is cached.")
    parser.add_argument("--folder_or_file_path", help="The folder or file path to check.")
    parser.add_argument("--force", action='store_true', help="Force reprocessing.")
    args = parser.parse_args()

    print(is_cached(args.folder_or_file_path, args.force))

'''
source venv/bin/activate
python lib_botrun/botrun_ask_folder/is_cached.py \
--folder_or_file_path "./data/1IpnZVKecvjcPOsH0q6YyhpS2ek2-Eig9/這是關於勞保的新聞資料.docx.txts"

'''
