import argparse
import os
import shutil
from typing import List
from botrun_ask_folder.constants import CHARS_PER_PAGE
from botrun_ask_folder.drive_download import truncate_filename

from botrun_ask_folder.models.drive_file import DriveFile

from .drive_download_metadata import (
    get_metadata_file_name,
    update_drive_file_after_process_file,
)
from .safe_join import safe_join
from .split_txts import (
    process_single_file,
    split_txts_no_threads,
    re_compile_page_number_pattern,
)


def find_files(input_folder: str) -> List[str]:
    splitted_file_pattern = re_compile_page_number_pattern()
    files_list = []
    metadata_file_name = get_metadata_file_name(input_folder)
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file == metadata_file_name:
                continue
            if not splitted_file_pattern.search(file):
                files_list.append(safe_join(root, file))
    return files_list


def run_split_txts(
    directory: str,
    chars_per_page: int,
    force: bool,
    gen_page_imgs: bool = False,
    new_items: list = None,
    google_drive_folder_id: str = None,
) -> None:
    """
    @param new_items: 這裡的 item的格式，是drive list 出來的結果，可以參考 metadata，如果是 None，執行的方式會照舊(目前應該是會有 bug，但是為不影響其它用到的地方)，如果有傳，包含空 list，會檢查在這個 list 裡的檔案才會進行更新
    """
    files = find_files(directory)
    output_folders = [f"{file_path}.txts" for file_path in files]
    if force:
        for folder_path in output_folders:
            try:
                shutil.rmtree(folder_path)
            except FileNotFoundError:
                pass
    try:
        split_txts_no_threads(
            source_files=files,
            output_folders=output_folders,
            chars_per_page=chars_per_page,
            force=force,
            gen_page_imgs=gen_page_imgs,
            metadata_dir=directory,
            new_items=new_items,
            google_drive_folder_id=None,
        )
    except Exception as e:
        print(f"Error processing files in {directory}")
        print(f"Exception: {e}")


async def run_split_txts_for_distributed(
    driveFile: DriveFile,
    chars_per_page: int = CHARS_PER_PAGE,
    force: bool = False,
) -> bool:
    """
    因為要分散執行，所以這邊的實作會牽涉到狀態的更新
    """
    ori_file_path = driveFile.save_path
    # todo implement force
    output_folder = f"{ori_file_path}.txts"
    try:
        lst_rag_metadata = process_single_file(
            ori_file_path,
            output_folder,
            chars_per_page,
            force,
            None,
        )
        await update_drive_file_after_process_file(driveFile, lst_rag_metadata)
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"run_split_txts_for_distributed generated an exception: {e}")
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自動掃描目錄並分頁處理文件")
    parser.add_argument("--input_folder", help="要掃描的目錄路徑")
    parser.add_argument("--chars_per_page", type=int, default=2000, help="每頁字符數量")
    parser.add_argument(
        "--force", action="store_true", help="強制重新處理文件，即使已經處理過"
    )
    args = parser.parse_args()

    run_split_txts(args.input_folder, args.chars_per_page, args.force)

"""
source venv/bin/activate
python lib_botrun/botrun_ask_folder/run_split_txts.py \
--input_folder "./data/1IpnZVKecvjcPOsH0q6YyhpS2ek2-Eig9"

"""
