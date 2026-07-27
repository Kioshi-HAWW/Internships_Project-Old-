"""
test_api.py — Unit/Integration tests for FastAPI endpoints (/health, /chat, /ingest).
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


@patch("app.services.agent_service.answer")
def test_chat_endpoint(mock_answer):
    mock_answer.return_value = {
        "answer": "The Third Door is about finding non-traditional paths.",
        "sources": [
            {
                "source_file": "The Third Door.pdf",
                "drive_link": "https://drive.google.com/file/d/123",
                "chunk_index": 0,
                "page": 1,
                "text_snippet": "There is always a third door...",
            }
        ],
    }

    response = client.post("/chat", json={"message": "What is the third door?"})
    assert response.status_code == 200
    data = response.json()
    assert "The Third Door" in data["answer"]
    assert len(data["sources"]) == 1
    assert data["sources"][0]["source_file"] == "The Third Door.pdf"


def test_chat_endpoint_validation():
    # Empty message should fail validation (422 Unprocessable Entity)
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 422


@patch("app.api.routes.ingest._run_ingestion")
def test_ingest_endpoint(mock_run_ingestion):
    response = client.post("/ingest")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "started"
    assert "running in background" in data["message"]
