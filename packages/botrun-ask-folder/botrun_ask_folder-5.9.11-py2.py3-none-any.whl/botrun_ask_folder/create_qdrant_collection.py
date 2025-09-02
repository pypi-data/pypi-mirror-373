# create_collection.py
import argparse
import asyncio

import dotenv
from qdrant_client import AsyncQdrantClient, models

from botrun_ask_folder.util.qdrant_util.create_payload_index import create_payload_index

dotenv.load_dotenv()


async def create_collection_with_client(client, collection_name, dimension=3072):
    try:
        await client.get_collection(collection_name)
        print(f"Collection '{collection_name}' already exists.")
    except Exception:
        await client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=dimension, distance=models.Distance.COSINE
            ),
        )
        print(f"Collection '{collection_name}' created with dimension {dimension}.")


async def create_qdrant_collection(
    collection_name, dimension, qdrant_host, qdrant_port
):
    client = AsyncQdrantClient(host=qdrant_host, port=qdrant_port)
    await create_collection_with_client(client, collection_name, dimension)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a new collection in Qdrant database."
    )
    parser.add_argument(
        "--collection_name",
        type=str,
        default="my_collection",
        help="Name of the Qdrant collection.",
    )
    parser.add_argument(
        "--dimension",
        type=int,
        default=3072,
        help="Dimension of the vectors to be stored.",
    )
    parser.add_argument(
        "--qdrant_host",
        type=str,
        default="localhost",
        help="Host where Qdrant is running.",
    )
    parser.add_argument(
        "--qdrant_port", type=int, default=6333, help="Port where Qdrant is accessible."
    )
    args = parser.parse_args()
    asyncio.run(
        create_qdrant_collection(
            args.collection_name, args.dimension, args.qdrant_host, args.qdrant_port
        )
    )

"""
python create_collection.py
"""
