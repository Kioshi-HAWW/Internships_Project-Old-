"""
config.py — Single source of truth for all environment variables.
Rules: never call os.environ directly outside this file.
"""
import os
import base64
import json
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Gemini (chat / agent model) ─────────────────────────────────────────
    gemini_api_key: str
    gemini_model: str = "gemini-flash-latest"

    # ── Qdrant Cloud (vector store) ──────────────────────────────────────────
    qdrant_url: str          # e.g. https://xxx.us-east4-0.gcp.cloud.qdrant.io
    qdrant_api_key: str
    qdrant_collection_name: str = "library"

    # ── Google Drive (Service Account) ───────────────────────────────────────
    # Store the raw service-account JSON as a base64-encoded env var on Render.
    # Locally you can set GOOGLE_SERVICE_ACCOUNT_FILE to the path of your key JSON file,
    # or GOOGLE_SERVICE_ACCOUNT_JSON to the raw single-line JSON string.
    google_service_account_b64: str = ""    # base64-encoded JSON (Render)
    google_service_account_json: str = ""   # raw JSON string (local .env)
    google_service_account_file: str = ""   # path to service_account.json file
    google_drive_folder_id: str             # Drive folder to ingest from

    # ── Embedding model (local, no API key) ──────────────────────────────────
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # ── Chunking ─────────────────────────────────────────────────────────────
    chunk_size: int = 900          # tokens approx (chars × 0.75 rule of thumb)
    chunk_overlap: int = 150

    # ── Retrieval ─────────────────────────────────────────────────────────────
    retrieval_top_k: int = 6

    def get_service_account_info(self) -> dict:
        """
        Return the service account credential dict.
        Prefers base64-encoded var (for Render), then file path, then raw JSON string,
        and falls back to looking for a local 'service_account.json' file.
        """
        if self.google_service_account_b64:
            raw = base64.b64decode(self.google_service_account_b64).decode("utf-8")
            return json.loads(raw)
        
        if self.google_service_account_file and os.path.exists(self.google_service_account_file):
            with open(self.google_service_account_file, "r") as f:
                return json.load(f)
                
        if self.google_service_account_json:
            val = self.google_service_account_json.strip()
            if os.path.exists(val):
                with open(val, "r") as f:
                    return json.load(f)
            if val.startswith(("{", "[")):
                try:
                    return json.loads(val)
                except Exception:
                    pass

        # Fallback to local file in project root if it exists
        default_file = "service_account.json"
        if os.path.exists(default_file):
            with open(default_file, "r") as f:
                return json.load(f)

        raise ValueError(
            "No Google service account credentials found. "
            "Set GOOGLE_SERVICE_ACCOUNT_B64, GOOGLE_SERVICE_ACCOUNT_FILE, or GOOGLE_SERVICE_ACCOUNT_JSON."
        )


import functools

@functools.lru_cache(maxsize=1)
def get_settings() -> "Settings":
    """Return the cached Settings singleton. Call this instead of importing settings directly."""
    return Settings()


def _settings_proxy():
    """Module-level proxy — keeps `from app.core.config import settings` working in app code."""
    return get_settings()


class _SettingsProxy:
    """Transparent proxy so `settings.field` works without eagerly constructing Settings."""
    def __getattr__(self, item):
        return getattr(get_settings(), item)

    def __repr__(self):
        return repr(get_settings())


# Use `settings` everywhere in application code.
# Tests must call `get_settings.cache_clear()` after patching env vars.
settings: Settings = _SettingsProxy()  # type: ignore[assignment]
