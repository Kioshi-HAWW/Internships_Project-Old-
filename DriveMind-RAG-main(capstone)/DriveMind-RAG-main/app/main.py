"""
main.py — FastAPI application entrypoint.
Starts logging, creates the Qdrant collection on startup, and mounts all routes.
"""
import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.logging import setup_logging
from app.core.config import settings
from app.api.routes import health, chat, ingest
from app.services import vectorstore_service

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup / shutdown tasks."""
    logger.info("Starting RAG Assistant (model: %s)", settings.gemini_model)
    # Ensure Qdrant collection exists before any request hits
    try:
        vectorstore_service.ensure_collection()
    except Exception as exc:
        logger.error("Qdrant startup check failed: %s", exc)
    yield
    logger.info("RAG Assistant shutting down.")


app = FastAPI(
    title="Personal Library RAG Assistant",
    description="Ask questions answered from your Google Drive document library.",
    version="0.1.0",
    lifespan=lifespan,
)

# ── Mount routers ─────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(ingest.router)

logger.info("Routes registered: /health, /chat, /ingest")
