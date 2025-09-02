# query_page_range.py
# 波頁碼
import argparse

from qdrant_client import QdrantClient
from qdrant_client.http import models

from .split_txts import get_page_number_prefix, get_page_number


def create_qdrant_client(
    qdrant_host, qdrant_port, qdrant_api_key="", prefix=None, https=False
):
    return QdrantClient(
        host=qdrant_host,
        port=qdrant_port,
        api_key=qdrant_api_key,
        prefix=prefix,
        https=https,
    )


def perform_query(qdrant_client, collection_name, scroll_filter):
    return qdrant_client.scroll(
        collection_name=collection_name,
        scroll_filter=scroll_filter,
        limit=99999,
    )


def build_field_conditions(file_path_contains, page, keywords):
    must_conditions = [
        models.FieldCondition(
            key="file_path", match=models.MatchText(text=file_path_contains)
        ),
        models.FieldCondition(
            key="file_path",
            match=models.MatchText(text=f".{get_page_number_prefix()}{page}."),
        ),
    ]
    keyword_conditions = [
        models.FieldCondition(key="text_content", match=models.MatchText(text=keyword))
        for keyword in keywords
    ]
    return must_conditions + keyword_conditions


def query_page_range_with_qdrant_client(
    qdrant_client,
    collection_name,
    file_path_contains,
    start_page,
    end_page,
    keywords,
    is_print_text,
):
    # 建構範圍內每一頁的條件
    page_conditions = [
        models.Filter(must=build_field_conditions(file_path_contains, page, keywords))
        for page in range(start_page, end_page + 1)
    ]

    # 執行查詢
    results = perform_query(
        qdrant_client=qdrant_client,
        collection_name=collection_name,
        scroll_filter=models.Filter(should=[models.Filter(should=page_conditions)]),
    )

    # 取得所有結果，並根據頁碼進行排序
    sorted_results = sorted(
        results[0], key=lambda x: get_page_number(x.payload["file_path"])
    )

    print(
        "文件總頁數: ",
        get_max_page_number(qdrant_client, collection_name, file_path_contains),
    )

    # 遍歷排序後的結果
    for result in sorted_results:
        page_number = get_page_number(result.payload["file_path"])
        print("吻合條件頁碼:", page_number)
        if is_print_text:
            print("該頁內容:\n", result.payload["text_content"])


def get_max_page_number(qdrant_client, collection_name, file_path_contains):
    results = perform_query(
        qdrant_client=qdrant_client,
        collection_name=collection_name,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="file_path", match=models.MatchText(text=file_path_contains)
                )
            ]
        ),
    )
    max_page = 0
    for result in results[0]:
        current_page = get_page_number(result.payload["file_path"])
        if current_page > max_page:
            max_page = current_page
    return max_page


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--qdrant_host", type=str, default="qdrant")
    parser.add_argument("--qdrant_port", type=int, default=6333)
    parser.add_argument(
        "--collection_name", type=str, default="1_a3kY_i54kQzB-jCf8BZDTJlMKSJ_21A"
    )
    parser.add_argument("--file_path_contains", type=str, default="")
    parser.add_argument("--start_page", type=int, default=1)
    parser.add_argument("--end_page", type=int, default=10)
    parser.add_argument("--keywords", type=str, nargs="+", default=[])
    # 增加一個參數是，是否印出吻合條件的頁碼的內文
    parser.add_argument("--is_print_text", action="store_true", default=False)

    args = parser.parse_args()

    qdrant_client = create_qdrant_client(
        qdrant_host=args.qdrant_host, qdrant_port=args.qdrant_port
    )

    query_page_range_with_qdrant_client(
        qdrant_client=qdrant_client,
        collection_name=args.collection_name,
        file_path_contains=args.file_path_contains,
        start_page=args.start_page,
        end_page=args.end_page,
        keywords=args.keywords,
        is_print_text=args.is_print_text,
    )

"""
source venv/bin/activate
time python lib_botrun/botrun_ask_folder/query_page_range.py \
--qdrant_host localhost \
--qdrant_port 6333 \
--collection_name 1_a3kY_i54kQzB-jCf8BZDTJlMKSJ_21A \
--file_path_contains "附件2_教育部「Big Maker全國公共圖書館科技運用與創新實驗環境建置及服務精進計畫」" \
--start_page 1 \
--end_page 999 \
--keywords "執行策略" "方法" \
--print_text

source venv/bin/activate
time python lib_botrun/botrun_ask_folder/query_page_range.py \
--qdrant_host localhost \
--qdrant_port 6333 \
--collection_name 1_a3kY_i54kQzB-jCf8BZDTJlMKSJ_21A \
--file_path_contains "附件2_教育部「Big Maker全國公共圖書館科技運用與創新實驗環境建置及服務精進計畫」" \
--start_page 1 \
--end_page 999 \
--keywords "計畫目標"

"""
