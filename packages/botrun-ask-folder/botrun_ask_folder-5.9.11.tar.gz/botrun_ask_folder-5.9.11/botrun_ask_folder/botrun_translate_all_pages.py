# botrun_translate_all_pages.py
import argparse
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from litellm import completion
from pathlib import Path
from typing import List

from .split_txts import split_txts_no_threads, re_compile_page_number_pattern

load_dotenv()

DEFAULT_MODEL = "openai/gpt-4o-mini"
DEFAULT_MAX_THREADS = 30
DEFAULT_MAX_CHARS_PER_PAGE = None


def translate_text(text: str, model: str) -> str:
    response = completion(
        model=model,
        messages=[{"role": "user",
                   "content":
                       f"請翻譯為臺灣慣用語（不要中國大陸用語），要繁體中文，"
                       f"上下文不要多廢話，純粹給我翻譯就好:\n\n{text}"}]
    )
    result_str = response.choices[0].message.content
    return result_str


def sort_string_list_with_numbers(string_list):
    def extract_number(filename):
        match = re.search(r'page_(\d+)', filename)
        if match:
            return int(match.group(1))
        return 0  # 如果沒有找到數字，返回 0

    # 使用 extract_number 函數作為排序鍵
    return sorted(string_list, key=extract_number)


def translate_file(
        input_file: str,
        output_dir: str,
        model: str = DEFAULT_MODEL,
        max_threads: int = DEFAULT_MAX_THREADS,
        chars_per_page: int = DEFAULT_MAX_CHARS_PER_PAGE
) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    # 刪除翻譯的輸出目錄底下所有 .txt 檔案
    for file in Path(output_dir).glob("*.txt"):
        file.unlink()
    temp_output_dir = Path(output_dir) / "temp_split"
    temp_output_dir.mkdir(parents=True, exist_ok=True)
    # 刪除 split 暫存目錄底下所有檔案
    for file in temp_output_dir.glob("*"):
        file.unlink()

    split_txts_no_threads([input_file], [str(temp_output_dir)], chars_per_page, force=True)

    all_paths = temp_output_dir.glob("*")
    lst_str_paths = []
    for path in all_paths:
        lst_str_paths.append(str(path))
    lst_sorted_paths = sort_string_list_with_numbers(lst_str_paths)
    translated_pages = []
    # 使用多線程進行翻譯
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_page = {executor.submit(translate_text, Path(str_path).read_text(encoding='utf-8'), model): str_path
                          for str_path in lst_sorted_paths}
        for future in as_completed(future_to_page):
            a_page_path = future_to_page[future]
            translated_text = future.result()

            page_path = Path(a_page_path)
            # get page number
            page_number = int(page_path.name.split("_")[-1][:-4])

            # 保存單獨的分頁翻譯文件
            translated_page_file = Path(output_dir) / f"page_{page_number}_translated.txt"
            translated_page_file.write_text(translated_text, encoding='utf-8')
            translated_pages.append((page_number, translated_text))
            print(f"已翻譯第 {page_number} 頁")

    # 按頁碼排序翻譯後的頁面
    translated_pages.sort(key=lambda x: x[0])

    # 合併所有翻譯後的頁面
    output_file = Path(output_dir) / f"{Path(input_file).stem}_translated.txt"
    final_translated_text = ""
    with open(output_file, 'w', encoding='utf-8') as f:
        for page_number, translated_text in translated_pages:
            f.write(f"== 第 {page_number} 頁 ==\n\n")
            f.write(translated_text)
            f.write("\n\n")
            final_translated_text += f"== 第 {page_number} 頁 ==\n\n{translated_text}\n\n"
    print("== 所有翻譯已完成並合併 ==")
    print(final_translated_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, default="./data/botrun_translate_all_pages/input/input.pdf")
    parser.add_argument("--output_dir", type=str, default="./data/botrun_translate_all_pages/output")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--max_threads", type=int, default=DEFAULT_MAX_THREADS)
    parser.add_argument("--chars_per_page", type=int, default=2000)

    args = parser.parse_args()

    translate_file(args.input_file, args.output_dir, args.model, args.max_threads, args.chars_per_page)
