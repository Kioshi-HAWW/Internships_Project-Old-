"""
chunking_service.py — Split extracted text into overlapping chunks.
Uses LangChain's RecursiveCharacterTextSplitter (lightweight, local, free).
Each chunk carries full metadata so answers can be traced back to source.
"""
import logging
import uuid
from typing import List, Dict, Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings

logger = logging.getLogger(__name__)

_splitter: RecursiveCharacterTextSplitter | None = None


def _get_splitter() -> RecursiveCharacterTextSplitter:
    global _splitter
    if _splitter is None:
        _splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
    return _splitter



def split(text: str, file_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Split `text` into chunks and attach Drive metadata to each chunk.

    Returns a list of chunk dicts:
        {
            "id": str (uuid),
            "text": str,
            "source_file": str,
            "drive_file_id": str,
            "drive_link": str,
            "chunk_index": int,
            "page": None  (page-level tracking is PDF-only; extend later)
        }
    """
    raw_chunks = _get_splitter().split_text(text)
    chunks = []

    for i, chunk_text in enumerate(raw_chunks):
        chunks.append(
            {
                "id": str(uuid.uuid4()),
                "text": chunk_text,
                "source_file": file_meta.get("name", "unknown"),
                "drive_file_id": file_meta.get("id", ""),
                "drive_link": file_meta.get("webViewLink", ""),
                "chunk_index": i,
                "page": None,  # future: parse from PDF page breaks
            }
        )

    logger.debug(
        "Split '%s' into %d chunks (size~%d, overlap~%d)",
        file_meta.get("name"),
        len(chunks),
        settings.chunk_size,
        settings.chunk_overlap,
    )
    return chunks
