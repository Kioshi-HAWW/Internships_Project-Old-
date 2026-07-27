"""
embedding_service.py — Gemini API embeddings (models/text-embedding-004).
Switched from local sentence-transformers to Gemini API to avoid OOM on
Render free tier (512 MB RAM). Gemini embeddings are free-tier-compatible
and produce 768-dim vectors.
"""
import logging
from typing import List, Dict, Any

import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

_EMBED_MODEL = "models/gemini-embedding-001"
_VECTOR_DIM = 3072  # gemini-embedding-001 output dimension


def _configure_genai() -> None:
    """Configure the Gemini client once (idempotent)."""
    genai.configure(api_key=settings.gemini_api_key)


def embed_text(text: str) -> List[float]:
    """Embed a single string and return the float vector."""
    _configure_genai()
    result = genai.embed_content(
        model=_EMBED_MODEL,
        content=text,
        task_type="retrieval_document",
    )
    return result["embedding"]


def embed_query(text: str) -> List[float]:
    """Embed a query string (uses retrieval_query task type for better recall)."""
    _configure_genai()
    result = genai.embed_content(
        model=_EMBED_MODEL,
        content=text,
        task_type="retrieval_query",
    )
    return result["embedding"]


def embed_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add an 'embedding' key to each chunk dict.
    Batches the texts into a single API call to avoid 15 RPM Gemini rate limits.
    Returns the same list with embeddings attached.
    """
    if not chunks:
        return []

    _configure_genai()
    texts = [chunk["text"] for chunk in chunks]
    
    # Send the list of strings to embed_content directly
    batch_result = genai.embed_content(
        model=_EMBED_MODEL,
        content=texts,
        task_type="retrieval_document",
    )
    
    embeddings = batch_result["embedding"]
    
    result = []
    for chunk, emb in zip(chunks, embeddings):
        enriched = dict(chunk)
        enriched["embedding"] = emb
        result.append(enriched)
        
    return result
