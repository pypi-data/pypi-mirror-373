import argparse
import asyncio
import dotenv
import os
import qdrant_client
import uuid
import json
import re
from datetime import datetime
from litellm import aembedding, embedding
from pathlib import Path
from qdrant_client.http import models
from botrun_ask_folder.constants import QDRANT_ACTION_TIMEOUT
from botrun_ask_folder.models.drive_file import DriveFile

from botrun_ask_folder.models.rag_metadata import PAGE_NUMBER_NA
from botrun_ask_folder.models.splitted_file import SplittedFile
from botrun_ask_folder.remove_qdrant_collection import remove_collection_with_client
from botrun_ask_folder.services.drive.drive_factory import (
    drive_client_factory,
    splitted_file_store_factory,
)
from botrun_ask_folder.util.qdrant_util.create_payload_index import create_payload_index
from .drive_download_metadata import (
    get_drive_download_metadata,
    get_metadata_file_name,
)
from .create_qdrant_collection import create_collection_with_client
from .emoji_progress_bar import EmojiProgressBar
from .split_txts import get_page_number_prefix
from qdrant_client.http.models import PayloadSchemaType, CollectionStatus
from botrun_ask_folder.models.drive_folder import (
    DriveFolder as BotrunCollectionStatus,
)


dotenv.load_dotenv()


async def is_already_indexed(client, collection_name, text_content):
    try:
        search_response = await client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                should=[
                    models.FieldCondition(
                        key="text_content", match=models.MatchValue(value=text_content)
                    ),
                ]
            ),
            limit=1,
        )
        return len(search_response[0]) > 0
    except Exception as e:
        print(
            f"embeddings_to_qdrant.py, is_already_indexed 發生例外錯誤，參數如下：\n- client: {client}\n- collection_name: {collection_name}\n- text_content: {text_content}"
        )
        print(f"embeddings_to_qdrant.py, is_already_indexed 錯誤訊息：{e}")
        # 異常處理後，假設資料不存在
        return False


async def index_document(
    client, collection_name, document_data_payload, embeddings
) -> bool:
    try:
        await client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    payload=document_data_payload,
                    vector=embeddings,
                )
            ],
        )
        return True
    except Exception as e:
        print(
            f"embeddings_to_qdrant.py, index_document 上傳文件發生錯誤，參數如下：\n- client: {client}\n- collection_name: {collection_name}\n- document_data_payload: {document_data_payload}\n- embeddings: {embeddings}"
        )
        print(f"embeddings_to_qdrant.py, index_document 錯誤訊息：{e}")
        return False


DEFAULT_MAX_TEXT_ONE_PAGE = 5200


def generate_embedding_sync(model, texts):
    try:
        if len(texts) > DEFAULT_MAX_TEXT_ONE_PAGE:
            texts = texts[:DEFAULT_MAX_TEXT_ONE_PAGE]
        embedding_result = embedding(model=model, input=texts)
        return embedding_result
    except Exception as e:
        print(
            f"embeddings_to_qdrant.py, 生成嵌入發生錯誤，參數如下：\n- model: {model}\n- texts: {texts}"
        )
        print(f"embeddings_to_qdrant.py, generate_embedding_sync錯誤訊息：{e}")
        return {"data": [{"embedding": []}]}


async def generate_embedding_async(model, texts):
    try:
        # if texts len > DEFAULT_MAX_TEXT_ONE_PAGE, cut it
        if len(texts) > DEFAULT_MAX_TEXT_ONE_PAGE:
            texts = texts[:DEFAULT_MAX_TEXT_ONE_PAGE]
        embedding = await aembedding(model=model, input=texts)
        return embedding
    except Exception as e:
        print(
            f"embeddings_to_qdrant.py, 生成嵌入發生錯誤，參數如下：\n- model: {model}\n- texts: {texts}"
        )
        print(f"embeddings_to_qdrant.py, generate_embedding_async 錯誤訊息：{e}")
        # 返回一個空的嵌入結果以避免中斷流程
        return {"data": [{"embedding": []}]}


async def process_file(
    client,
    file_path,
    collection_name,
    model,
    semaphore,
    counters,
    progress_bar,
    dic_metadata={},
    # splitted_items: dict[str, SplittedFile] = None,
):
    async with semaphore:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text_content = f.read()

            if await is_already_indexed(client, collection_name, text_content):
                counters["skipped_count"] += 1
            else:
                embeddings_response = await generate_embedding_async(
                    model, [f"{file_path} {text_content}"]
                )
                embeddings = embeddings_response["data"][0]["embedding"]

                document_data_payload = {
                    "text_content": text_content,
                    "file_path": str(file_path),
                }
                if dic_metadata:
                    for item in dic_metadata["items"]:
                        if item["name"] == file_path.name:
                            document_data_payload["google_file_id"] = item["id"]
                            document_data_payload["gen_page_imgs"] = item[
                                "gen_page_imgs"
                            ]
                            document_data_payload["ori_file_name"] = item[
                                "ori_file_name"
                            ]
                            if (
                                "page_number" in item.keys()
                                and item["page_number"] != PAGE_NUMBER_NA
                            ):
                                document_data_payload["page_number"] = item[
                                    "page_number"
                                ]
                            if "sheet_name" in item.keys():
                                document_data_payload["sheet_name"] = item["sheet_name"]
                            if "modifiedTime" in item.keys():
                                document_data_payload["file-upload-date"] = item[
                                    "modifiedTime"
                                ]
                            break

                await index_document(
                    client, collection_name, document_data_payload, embeddings
                )
                counters["added_count"] += 1
            progress_bar.update(counters["skipped_count"] + counters["added_count"])
        except Exception as e:
            print(f"embeddings_to_qdrant.py, 處理文件發生錯誤，文件路徑：{file_path}")
            print(f"embeddings_to_qdrant.py, process_file 錯誤訊息：{e}")


async def process_split_file_for_distributed(
    client,
    split_file: SplittedFile,
    collection_name,
    model,
    semaphore,
) -> bool:
    """
    這一段是給 fastapi 用的
    """
    print(
        f"embeddings_to_qdrant_distributed {split_file.id} start, ori_file_id: {split_file.file_id}"
    )
    async with semaphore:
        retry_count = 10
        success = False
        while not success and retry_count > 0:
            try:
                with open(split_file.save_path, "r", encoding="utf-8") as f:
                    text_content = f.read()

                if await is_already_indexed(client, collection_name, text_content):
                    print(
                        f"embeddings_to_qdrant_distributed {split_file.id} already indexed, return True,"
                        f"ori_file_id: {split_file.file_id}"
                    )
                    return True
                else:
                    print(
                        f"embeddings_to_qdrant_distributed {split_file.id} start embedding, "
                        f"ori_file_id: {split_file.file_id}"
                    )
                    embeddings_response = await generate_embedding_async(
                        model, [f"{split_file.save_path} {text_content}"]
                    )
                    embeddings = embeddings_response["data"][0]["embedding"]
                    print(
                        f"embeddings_to_qdrant_distributed {split_file.id} end embedding, "
                        f"ori_file_id: {split_file.file_id}"
                    )

                    document_data_payload = {
                        "text_content": text_content,
                        "file_path": str(split_file.name),
                    }
                    document_data_payload["google_file_id"] = split_file.file_id
                    document_data_payload["gen_page_imgs"] = split_file.gen_page_imgs
                    document_data_payload["page_number"] = split_file.page_number
                    document_data_payload["sheet_name"] = split_file.sheet_name
                    document_data_payload["file-upload-date"] = split_file.modified_time
                    document_data_payload["ori_file_name"] = split_file.ori_file_name
                    if starts_with_date_format(split_file.ori_file_name) is not None:
                        year, month, day = starts_with_date_format(
                            split_file.ori_file_name
                        )
                        document_data_payload["roc-date"] = (
                            f"{year-1911}年{month}月{day}日"
                        )
                        document_data_payload["ad-date"] = f"{year}年{month}月{day}日"

                    success = await index_document(
                        client, collection_name, document_data_payload, embeddings
                    )
                    print(
                        f"embeddings_to_qdrant_distributed {split_file.id} end indexing success: {success}, "
                        f"ori_file_id: {split_file.file_id}"
                    )
                    if not success:
                        retry_count -= 1
                        await asyncio.sleep(3)
                        continue
                    else:
                        print(
                            f"embeddings_to_qdrant_distributed {split_file.id} return True, "
                            f"ori_file_id: {split_file.file_id}"
                        )
                        return True
            except Exception as e:
                print(
                    f"embeddings_to_qdrant.py, 處理文件發生錯誤，文件路徑：{split_file.save_path}, ori_file_id: {split_file.file_id}"
                )
                print(
                    f"embeddings_to_qdrant.py, ori_file_id: {split_file.file_id} 錯誤訊息：{e}"
                )
                retry_count -= 1
                await asyncio.sleep(3)
                continue
        print(
            f"embeddings_to_qdrant_distributed {split_file.id} final success: {success}, "
            f"ori_file_id: {split_file.file_id}"
        )
        return success


def starts_with_date_format(input_string):
    # 正則表達式模式匹配 YYYY-MM-DD_ 或 YYYY-MM-DD- 格式
    # 支援月份和日期可能有前導零也可能沒有
    pattern = r"(\d{4})-(\d{1,2})-(\d{1,2})[_-]"

    match = re.search(pattern, input_string)

    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))

        return (year, month, day)
    else:
        return None  # 如果沒有匹配到合適的日期格式，返回None


def count_txt_files(input_folder):
    total_files = 0
    try:
        for _, _, files in os.walk(input_folder):
            for file in files:
                if get_page_number_prefix() in file:
                    total_files += 1
    except Exception as e:
        print(
            f"embeddings_to_qdrant.py, 計算文件數目發生錯誤，資料夾路徑：{input_folder}"
        )
        print(f"embeddings_to_qdrant.py, count_txt_files 錯誤訊息：{e}")
    return total_files


async def has_collection_in_qdrant(
    collection_name,
    qdrant_host,
    qdrant_port,
    qdrant_api_key,
    qdrant_prefix,
    qdrant_https,
):
    try:

        client = qdrant_client.AsyncQdrantClient(
            qdrant_host,
            port=qdrant_port,
            timeout=QDRANT_ACTION_TIMEOUT,
            api_key=qdrant_api_key,
            prefix=qdrant_prefix,
            https=qdrant_https,
        )
        await client.get_collection(collection_name)
        return True
    except Exception as e:
        return False


async def embeddings_to_qdrant(
    input_folder,
    model,
    dimension,
    max_tasks,
    collection_name,
    qdrant_host,
    qdrant_port,
    qdrant_api_key,
    force=False,
    qdrant_prefix=None,
    qdrant_https=False,
):
    try:
        client = qdrant_client.AsyncQdrantClient(
            qdrant_host,
            port=qdrant_port,
            api_key=qdrant_api_key,
            prefix=qdrant_prefix,
            https=qdrant_https,
        )
        if force:
            await remove_collection_with_client(client, collection_name)
        semaphore = asyncio.Semaphore(max_tasks)
        await create_collection_with_client(client, collection_name, dimension)
        try:
            await create_payload_index(client, collection_name, "file-upload-date")
        except Exception as e:
            print("這一段是開發在用的，prod 要拿掉，雖然有錯，但是不影響功能")
            import traceback

            print(traceback.format_exc())

        while True:
            status = await client.get_collection(collection_name)
            if status.status == CollectionStatus.GREEN:
                break
            print("等待索引建立完成...")
            await asyncio.sleep(1)

        counters = {"skipped_count": 0, "added_count": 0}
        tasks = []
        # print start this process
        print("== Starting the embedding to Qdrant ==")
        progress_bar = EmojiProgressBar(count_txt_files(input_folder))
        int_txt_files_count = 0
        metadata_file_name = get_metadata_file_name(input_folder)
        dic_metadata = get_drive_download_metadata(input_folder)
        # drive_client = drive_client_factory()
        # split_files = await drive_client.get_split_files(collection_name)

        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file == metadata_file_name:
                    continue
                if get_page_number_prefix() in file:
                    file_path = Path(root) / file
                    task = process_file(
                        client,
                        file_path,
                        collection_name,
                        model,
                        semaphore,
                        counters,
                        progress_bar,
                        dic_metadata,
                        # split_files,
                    )
                    tasks.append(task)
                    int_txt_files_count += 1

        await asyncio.gather(*tasks)
        print(
            f"embeddings_to_qdrant_txt.py, "
            f"skipped: {counters['skipped_count']}, "
            f"added to qdrant: {counters['added_count']}"
        )
    except Exception as e:
        print(
            f"embeddings_to_qdrant.py, 處理資料夾發生錯誤，參數如下：\n- input_folder: {input_folder}\n- model: {model}\n- dimension: {dimension}\n- max_tasks: {max_tasks}\n- collection_name: {collection_name}\n- qdrant_host: {qdrant_host}\n- qdrant_port: {qdrant_port}"
        )
        print(f"embeddings_to_qdrant.py, embeddings_to_qdrant 錯誤訊息：{e}")


async def init_qdrant_collection(
    collection_name: str,
    dimension=3072,
    force=False,
    qdrant_host="qdrant",
    qdrant_port=6333,
    qdrant_api_key="",
    qdrant_prefix=None,
    qdrant_https=False,
):
    try:
        client = qdrant_client.AsyncQdrantClient(
            qdrant_host,
            port=qdrant_port,
            timeout=QDRANT_ACTION_TIMEOUT,
            api_key=qdrant_api_key,
            prefix=qdrant_prefix,
            https=qdrant_https,
        )
        if force:
            await remove_collection_with_client(client, collection_name)

        collection_existed = await has_collection_in_qdrant(
            f"{collection_name}",
            qdrant_host,
            qdrant_port,
            qdrant_api_key,
            qdrant_prefix,
            qdrant_https,
        )

        if not collection_existed:
            await create_collection_with_client(client, collection_name, dimension)

        try:
            await create_payload_index(client, collection_name, "file-upload-date")
        except Exception as e:
            print("這一段是開發在用的，prod 要拿掉，雖然有錯，但是不影響功能")
            import traceback

            print(traceback.format_exc())

        while True:
            status = await client.get_collection(collection_name)
            if status.status == CollectionStatus.GREEN:
                break
            print("等待索引建立完成...")
            await asyncio.sleep(1)

    except Exception as e:
        print(
            f"init_qdrant_collection, 發生錯誤，參數如下：\n- dimension: {dimension}\n- collection_name: {collection_name}\n- qdrant_host: {qdrant_host}\n- qdrant_port: {qdrant_port}"
        )
        import traceback

        print(traceback.format_exc())
        print(f"init_qdrant_collection, 錯誤訊息：{e}")


async def embeddings_to_qdrant_distributed(
    drive_file: DriveFile,
    model="openai/text-embedding-3-large",
    dimension=3072,
    max_tasks=30,
    qdrant_host="qdrant",
    qdrant_port=6333,
    qdrant_api_key="",
    qdrant_prefix=None,
    qdrant_https=False,
) -> bool:
    try:
        print(f"embeddings_to_qdrant_distributed function start {drive_file.id}")
        client = qdrant_client.AsyncQdrantClient(
            qdrant_host,
            port=qdrant_port,
            timeout=QDRANT_ACTION_TIMEOUT,
            api_key=qdrant_api_key,
            prefix=qdrant_prefix,
            https=qdrant_https,
        )
        semaphore = asyncio.Semaphore(max_tasks)

        tasks = []
        print("== Starting the embedding to Qdrant ==")
        split_file_store = splitted_file_store_factory()

        for split_file_id in drive_file.splitted_files:
            split_file = await split_file_store.get_splitted_file(split_file_id)
            task = process_split_file_for_distributed(
                client,
                split_file,
                drive_file.folder_id,
                model,
                semaphore,
            )
            tasks.append(task)

        # print(f"embeddings_to_qdrant_distributed {drive_file.id} start embedding")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # print(f"embeddings_to_qdrant_distributed {drive_file.id} end embedding")

        success_count = sum(1 for result in results if result is True)
        # print(
        #     f"embeddings_to_qdrant_distributed {drive_file.id} success count: {success_count}"
        # )
        failure_count = len(results) - success_count
        # print(
        #     f"embeddings_to_qdrant_distributed {drive_file.id} failure count: {failure_count}"
        # )
        if failure_count > 0:
            print(f"embeddings_to_qdrant_distributed {drive_file.id} failed")
        print(f"embeddings_to_qdrant_distributed {drive_file.id} completed")
        # print(f"Successful tasks: {success_count}")
        # print(f"Failed tasks: {failure_count}")

        return failure_count == 0  # Return True if all tasks succeeded, False otherwise
    except Exception as e:
        print(
            f"embeddings_to_qdrant_distributed, file_id: {drive_file.id} 處理資料夾發生錯誤，參數如下：\n- model: {model}\n- dimension: {dimension}\n- max_tasks: {max_tasks}\n- collection_name: {drive_file.folder_id}\n- qdrant_host: {qdrant_host}\n- qdrant_port: {qdrant_port}"
        )
        import traceback

        print(traceback.format_exc())
        print(
            f"embeddings_to_qdrant_distributed, file_id: {drive_file.id} 錯誤訊息：{e}"
        )
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Index documents into Qdrant with embeddings."
    )
    parser.add_argument("--input_folder", default="./data")
    parser.add_argument("--model", default="openai/text-embedding-3-large")
    parser.add_argument("--dimension", type=int, default=3072)
    parser.add_argument("--max_tasks", type=int, default=30)
    parser.add_argument("--collection_name", type=str, default="collection_3")
    parser.add_argument("--qdrant_host", type=str, default=None)  # 新增參數
    parser.add_argument("--qdrant_port", type=int, default=None)  # 新增參數
    args = parser.parse_args()
    # 如果指定了命令列參數，則使用它們；否則從環境變數或使用默認值
    qdrant_host = (
        args.qdrant_host
        if args.qdrant_host is not None
        else os.getenv("QDRANT_HOST", "localhost")
    )
    qdrant_port = (
        args.qdrant_port
        if args.qdrant_port is not None
        else int(os.getenv("QDRANT_PORT", "6333"))
    )
    try:
        asyncio.run(
            embeddings_to_qdrant(
                args.input_folder,
                args.model,
                args.dimension,
                args.max_tasks,
                args.collection_name,
                qdrant_host,
                qdrant_port,
            )
        )
    except Exception as e:
        print(
            f"embeddings_to_qdrant.py, 主程序發生錯誤，參數如下：\n- input_folder: {args.input_folder}\n- model: {args.model}\n- dimension: {args.dimension}\n- max_tasks: {args.max_tasks}\n- collection_name: {args.collection_name}\n- qdrant_host: {qdrant_host}\n- qdrant_port: {qdrant_port}"
        )
        print(f"embeddings_to_qdrant.py, main 錯誤訊息：{e}")

"""
source venv/bin/activate
python lib_botrun/botrun_ask_folder/embeddings_to_qdrant.py \
--input_folder "./data/1IpnZVKecvjcPOsH0q6YyhpS2ek2-Eig9" \
--model "openai/text-embedding-3-large" \
--dimension 3072 \
--collection_name "1IpnZVKecvjcPOsH0q6YyhpS2ek2-Eig9" \
--qdrant_host "localhost" \
--qdrant_port 6333
"""
