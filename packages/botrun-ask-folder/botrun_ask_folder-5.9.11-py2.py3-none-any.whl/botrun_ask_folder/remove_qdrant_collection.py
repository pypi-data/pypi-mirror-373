from dotenv import load_dotenv
from qdrant_client import AsyncQdrantClient

load_dotenv()


async def remove_collection_with_client(client: AsyncQdrantClient, collection_name: str):
    try:
        await client.delete_collection(collection_name=collection_name)
        print(f"Collection '{collection_name}' deleted successfully.")
    except Exception as e:
        print(f"Failed to delete collection '{collection_name}': {e}")
