from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PayloadSchemaType



async def create_payload_index(client: AsyncQdrantClient, collection_name: str, field_name:str) -> None:
    """
    Create payload index for collection
    :param client: qdrant client
    :param collection_name: collection name
    :param payload: payload to create index
    :return: None
    """
    await client.create_payload_index(
        collection_name=collection_name,
        field_name=field_name,
        field_schema=PayloadSchemaType.DATETIME,
    )


