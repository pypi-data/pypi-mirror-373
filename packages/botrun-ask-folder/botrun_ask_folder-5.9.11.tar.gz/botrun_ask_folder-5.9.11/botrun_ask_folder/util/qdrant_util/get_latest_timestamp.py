import os
from typing import Union

from qdrant_client.http.models import (
    FieldCondition,
    Range,
    OrderBy,
    Filter,
    IsEmptyCondition,
    PayloadField,
)
from qdrant_client import AsyncQdrantClient
from datetime import datetime
import pytz
import qdrant_client


async def get_latest_timestamp(
    collection_name: str,
) -> Union[str, None]:
    try:
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = os.getenv("QDRANT_PORT", 6333)
        qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
        qdrant_prefix = os.getenv("QDRANT_PREFIX", None)
        qdrant_https = os.getenv("QDRANT_HTTPS", "False").lower() == "true"
        client = qdrant_client.AsyncQdrantClient(
            qdrant_host,
            port=qdrant_port,
            api_key=qdrant_api_key,
            prefix=qdrant_prefix,
            https=qdrant_https,
        )
        latest_time = await get_latest_timestamp_with_client(client, collection_name)
        if latest_time is not None:
            print(f"最新的資料時間是: {latest_time}")
            return latest_time
    except:
        return None


async def get_latest_timestamp_with_client(
    client: AsyncQdrantClient,
    collection_name: str,
    timestamp_field: str = "file-upload-date",
):
    try:
        # 檢查集合中的點數
        collection_info = await client.get_collection(collection_name)
        points_count = collection_info.points_count
        # print(f"集合 '{collection_name}' 中有 {points_count} 個點")

        if points_count == 0:
            print("集合為空")
            return None

        # 使用 Qdrant 的排序功能獲取最新的記錄
        search_result = await client.scroll(
            collection_name=collection_name,
            scroll_filter=Filter(
                must_not=[
                    IsEmptyCondition(
                        is_empty=PayloadField(key=timestamp_field),
                    )
                ]
            ),
            limit=1,
            with_payload=True,
            with_vectors=False,
            order_by=OrderBy(key=timestamp_field, direction="desc"),
        )

        if not search_result[0]:
            print(
                "系統找不到含有時間資訊的欄位，若您需要查詢最後更新時間，請重新建立此知識庫"
            )
            return None

        latest_point = search_result[0][0]
        timestamp_str = latest_point.payload.get(timestamp_field)

        if not timestamp_str:
            print(
                "系統找不到含有時間資訊的欄位，若您需要查詢最後更新時間，請重新建立此知識庫"
            )
            return None

        try:
            latest_datetime = datetime.fromisoformat(
                timestamp_str.replace("Z", "+00:00")
            )
        except ValueError as e:
            print(f"無法解析時間戳 '{timestamp_str}': {e}")
            return None

        # 將 UTC 時間轉換為本地時間
        local_time = latest_datetime.replace(tzinfo=pytz.UTC).astimezone(
            pytz.timezone("Asia/Taipei")
        )
        readable_time = local_time.strftime("%Y-%m-%d %H:%M:%S %Z")

        return readable_time

    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        return None
