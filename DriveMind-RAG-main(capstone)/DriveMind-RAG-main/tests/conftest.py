# conftest.py — shared pytest fixtures (extend as needed)
import pytest
import os


@pytest.fixture(autouse=True)
def _no_real_env(monkeypatch):
    """
    Prevent tests from accidentally reading a real .env and hitting live services.
    Sets required env vars BEFORE the settings proxy is first accessed,
    and clears the lru_cache so each test gets a fresh Settings object.
    """
    # Set required env vars
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_API_KEY", "test-qdrant-key")
    monkeypatch.setenv("GOOGLE_DRIVE_FOLDER_ID", "test-folder-id")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{}")

    # Clear the cached Settings instance so the proxy rebuilds with test values
    from app.core.config import get_settings
    get_settings.cache_clear()

    yield

    # Clear again after test so next test starts fresh
    get_settings.cache_clear()
