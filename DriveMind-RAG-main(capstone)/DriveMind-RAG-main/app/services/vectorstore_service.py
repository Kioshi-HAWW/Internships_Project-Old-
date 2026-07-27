"""
vectorstore_service.py — Qdrant Cloud client wrapper.
Handles upsert + similarity search with metadata.
Client is instantiated once (FastAPI dependency pattern — see main.py).
"""
import logging
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
)

from app.core.config import settings
from app.services.embedding_service import embed_query

logger = logging.getLogger(__name__)

# Singleton Qdrant client
_client: QdrantClient | None = None

# Dimension for Gemini gemini-embedding-001
VECTOR_SIZE = 3072


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        logger.info("Connecting to Qdrant at %s", settings.qdrant_url)
        _client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=60.0,
        )
    return _client


def ensure_collection() -> None:
    """Create the Qdrant collection if it doesn't already exist."""
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]

    if settings.qdrant_collection_name not in existing:
        logger.info(
            "Creating Qdrant collection '%s'", settings.qdrant_collection_name
        )
        client.create_collection(
            collection_name=settings.qdrant_collection_name,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
    else:
        logger.info(
            "Qdrant collection '%s' already exists.", settings.qdrant_collection_name
        )


def upsert(chunks: List[Dict[str, Any]], batch_size: int = 50) -> None:
    """
    Upsert a list of embedded chunks into Qdrant.
    Each chunk must have 'id', 'embedding', and all metadata keys.
    Splits the points into batches to prevent request timeouts.
    """
    client = get_client()
    points = [
        PointStruct(
            id=chunk["id"],
            vector=chunk["embedding"],
            payload={
                "text": chunk["text"],
                "source_file": chunk["source_file"],
                "drive_file_id": chunk["drive_file_id"],
                "drive_link": chunk["drive_link"],
                "chunk_index": chunk["chunk_index"],
                "page": chunk["page"],
            },
        )
        for chunk in chunks
    ]

    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        client.upsert(
            collection_name=settings.qdrant_collection_name,
            points=batch,
        )
        logger.info("Upserted batch of %d points to Qdrant (%d/%d total).", len(batch), min(i + batch_size, len(points)), len(points))
    logger.debug("Successfully upserted all %d points.", len(points))


def search(query: str, top_k: int | None = None) -> List[Dict[str, Any]]:
    """
    Embed `query` and return the top-k most similar chunks with metadata.
    Returns a list of payload dicts enriched with a 'score' key.
    """
    k = top_k or settings.retrieval_top_k
    client = get_client()
    query_vector = embed_query(query)

    hits = client.search(
        collection_name=settings.qdrant_collection_name,
        query_vector=query_vector,
        limit=k,
        with_payload=True,
    )

    results = []
    for hit in hits:
        payload = dict(hit.payload)
        payload["score"] = hit.score
        results.append(payload)

    logger.info(
        "search_library('%s') -> %d results (top score: %.3f)",
        query[:60],
        len(results),
        results[0]["score"] if results else 0,
    )
    return results
