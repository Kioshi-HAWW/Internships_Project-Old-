"""
test_chunking.py — Unit tests for chunking_service.
"""
import pytest
from app.services.chunking_service import split


FAKE_META = {
    "id": "fake_drive_id",
    "name": "test_document.txt",
    "mimeType": "text/plain",
    "webViewLink": "https://drive.google.com/fake",
}


def test_split_produces_chunks():
    text = "Hello world. " * 200  # ~2600 chars
    chunks = split(text, FAKE_META)
    assert len(chunks) > 1


def test_chunk_has_required_keys():
    text = "Some content for the test. " * 100
    chunks = split(text, FAKE_META)
    required = {"id", "text", "source_file", "drive_file_id", "drive_link", "chunk_index"}
    for chunk in chunks:
        assert required.issubset(chunk.keys()), f"Missing keys in chunk: {chunk.keys()}"


def test_chunk_metadata_matches_file_meta():
    text = "Content. " * 100
    chunks = split(text, FAKE_META)
    for chunk in chunks:
        assert chunk["source_file"] == FAKE_META["name"]
        assert chunk["drive_file_id"] == FAKE_META["id"]
        assert chunk["drive_link"] == FAKE_META["webViewLink"]


def test_chunk_indexes_are_sequential():
    text = "Word " * 500
    chunks = split(text, FAKE_META)
    for i, chunk in enumerate(chunks):
        assert chunk["chunk_index"] == i


def test_empty_text_returns_no_chunks():
    chunks = split("", FAKE_META)
    assert chunks == []
