import argparse
from qdrant_client import QdrantClient
from qdrant_client import models
from typing import Dict, List, Any

from .embeddings_to_qdrant import generate_embedding_sync


def query_qdrant_rerank(
    qdrant_host: str,
    qdrant_port: int,
    collection_name: str,
    user_input: str,
    embedding_model: str,
    top_k: int,
    hnsw_ef: int,
    file_path_field: str = "file_path",
    text_content_field: str = "text_content",
    qdrant_api_key: str = "",
    prefix=None,
    https=False,
) -> Dict[str, Any]:
    qdrant_client_instance: QdrantClient = QdrantClient(
        qdrant_host,
        port=qdrant_port,
        api_key=qdrant_api_key,
        prefix=prefix,
        https=https,
    )
    query_vector: Dict[str, List[Dict[str, List[float]]]] = generate_embedding_sync(
        embedding_model, user_input
    )
    search_params: models.SearchParams = models.SearchParams(
        hnsw_ef=hnsw_ef, exact=False
    )
    search_result: List[models.ScoredPoint] = qdrant_client_instance.search(
        collection_name=collection_name,
        query_vector=query_vector["data"][0]["embedding"],
        search_params=search_params,
        limit=top_k,
        with_payload=True,
    )
    return {
        "search_result": search_result,
        "file_path_field": file_path_field,
        "text_content_field": text_content_field,
    }


def print_results(result: Dict[str, Any], user_input: str, top_k: int) -> None:
    print(f"Top {top_k} results for query: '{user_input}'")
    print("-" * 50)
    for idx, hit in enumerate(result["search_result"], start=1):
        file_path: str = hit.payload.get(result["file_path_field"], "N/A")
        score: float = hit.score
        print(f"單純流水號 {idx}:")
        # print(f"  {result['file_path_field']}: {file_path}")
        print(
            f"  {result['text_content_field']}: {hit.payload.get(result['text_content_field'], 'N/A')[0:200]}..."
        )
        # print(f"  Relevance Score: {score:.4f}")
        print("-" * 50)


def main() -> None:
    print("🈯️let us start query_qdrant_rerank.py")
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Query Qdrant and rerank results"
    )
    parser.add_argument("--qdrant_host", type=str, default="localhost")
    parser.add_argument("--qdrant_port", type=int, default=6333)
    parser.add_argument("--collection_name", type=str, default="medium_bohachu")
    parser.add_argument("--user_input", type=str, default="claude")
    parser.add_argument(
        "--embedding_model", type=str, default="openai/text-embedding-3-large"
    )
    parser.add_argument("--top_k", type=int, default=30)
    parser.add_argument("--hnsw_ef", type=int, default=256)
    parser.add_argument("--file_path_field", type=str, default="title")
    parser.add_argument("--text_content_field", type=str, default="content")
    args: argparse.Namespace = parser.parse_args()

    result: Dict[str, Any] = query_qdrant_rerank(
        qdrant_host=args.qdrant_host,
        qdrant_port=args.qdrant_port,
        collection_name=args.collection_name,
        user_input=args.user_input,
        embedding_model=args.embedding_model,
        top_k=args.top_k,
        hnsw_ef=args.hnsw_ef,
        file_path_field=args.file_path_field,
        text_content_field=args.text_content_field,
    )

    print_results(result, args.user_input, args.top_k)


if __name__ == "__main__":
    main()
