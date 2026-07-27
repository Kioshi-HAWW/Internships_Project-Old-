"""
test_vectorstore.py — Tests for vectorstore_service using a mock Qdrant client.
"""
import pytest
from unittest.mock import MagicMock, patch


SAMPLE_CHUNKS = [
    {
        "id": "chunk-001",
        "text": "Python is a high-level programming language.",
        "embedding": [0.1] * 384,
        "source_file": "python_guide.pdf",
        "drive_file_id": "abc",
        "drive_link": "https://drive.google.com/abc",
        "chunk_index": 0,
        "page": None,
    }
]


@patch("app.services.vectorstore_service.get_client")
def test_upsert_calls_qdrant(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    from app.services.vectorstore_service import upsert
    upsert(SAMPLE_CHUNKS)

    mock_client.upsert.assert_called_once()
    call_kwargs = mock_client.upsert.call_args.kwargs
    assert call_kwargs["collection_name"] is not None
    assert len(call_kwargs["points"]) == 1


@patch("app.services.vectorstore_service.embed_text")
@patch("app.services.vectorstore_service.get_client")
def test_search_returns_payloads(mock_get_client, mock_embed):
    mock_embed.return_value = [0.1] * 384

    mock_hit = MagicMock()
    mock_hit.score = 0.95
    mock_hit.payload = {
        "text": "Python is great.",
        "source_file": "guide.pdf",
        "drive_link": "https://drive.google.com/x",
        "chunk_index": 0,
        "page": None,
    }
    mock_client = MagicMock()
    mock_client.search.return_value = [mock_hit]
    mock_get_client.return_value = mock_client

    from app.services.vectorstore_service import search
    results = search("What is Python?", top_k=3)

    assert len(results) == 1
    assert results[0]["source_file"] == "guide.pdf"
    assert results[0]["score"] == 0.95
