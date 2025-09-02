"""
python lib_botrun/botrun_ask_folder/pipeline_drive_query.py \
--service_account_file "./keys/google_service_account_key.json" \
--google_drive_url "https://drive.google.com/drive/folders/1XAvwtdr9NBQy3adrghPSP9O7rdo0CEHQ?usp=sharing" \
--user_query "我想問幸福花園專案是什麼東西？" \
--download_folder "./data/波通鑑測試"
"""

import argparse
import asyncio
import sys

from .drive_list_files import drive_list_files
from .drive_list_files import extract_folder_id
from .run_split_txts import run_split_txts
from .drive_download import drive_download
from .embeddings_to_qdrant import embeddings_to_qdrant
from .query_qdrant import query_qdrant_and_llm


def pipeline_drive_query(
    service_account_file, google_drive_url, user_query, download_folder
):
    folder_id = extract_folder_id(google_drive_url)

    drive_list_files(service_account_file, folder_id, max_files=None)

    drive_download(
        service_account_file,
        folder_id,
        max_files=None,
        output_folder=download_folder,
        force=False,
    )

    run_split_txts(download_folder, chars_per_page=2000, force=False)

    collection_name = folder_id  # Use the folder ID as the collection name for Qdrant
    # 目前這裡應該會出錯，但是應該沒有呼叫到，暫時保留
    asyncio.run(
        embeddings_to_qdrant(
            input_folder=download_folder,
            model="openai/text-embedding-3-large",
            dimension=3072,
            max_tasks=30,
            collection_name=collection_name,
        )
    )

    qdrant_host = "localhost"
    qdrant_port = 6333
    embedding_model = "openai/text-embedding-3-large"
    top_k = 12
    notice_prompt = """
    請妳使用繁體中文回答，必須使用臺灣慣用語回答
    請妳不可以使用簡體中文回答，不可以使用大陸慣用語回答
    回答的最末端尾巴要附上妳引證的來源檔案名稱
    如果妳不會回答的部分，不可以亂猜
    """
    chat_model = "gpt-4-turbo-preview"
    hnsw_ef = 256

    for response in query_qdrant_and_llm(
        qdrant_host=qdrant_host,
        qdrant_port=qdrant_port,
        collection_name=collection_name,
        user_input=user_query,
        embedding_model=embedding_model,
        top_k=top_k,
        notice_prompt=notice_prompt,
        chat_model=chat_model,
        hnsw_ef=hnsw_ef,
    ):
        print(response, end="")
        sys.stdout.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline to fetch from Drive, process, and query via Qdrant."
    )
    parser.add_argument(
        "--service_account_file",
        required=True,
        help="Path to the service account credentials file.",
    )
    parser.add_argument(
        "--google_drive_url", required=True, help="URL of the Google Drive folder."
    )
    parser.add_argument(
        "--user_query", required=True, help="User query to search in documents."
    )
    parser.add_argument(
        "--download_folder",
        default="./data",
        help="Output folder for downloaded and processed files.",
    )

    args = parser.parse_args()

    pipeline_drive_query(
        args.service_account_file,
        args.google_drive_url,
        args.user_query,
        args.download_folder,
    )
