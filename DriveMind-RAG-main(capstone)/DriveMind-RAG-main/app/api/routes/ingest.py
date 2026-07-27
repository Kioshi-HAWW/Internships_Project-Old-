"""
ingest.py — POST /ingest
Triggers a Drive sync + embedding run (manually called, not scheduled — free plan).
"""
import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.schemas import IngestResponse
from app.services import drive_service, chunking_service, embedding_service, vectorstore_service

logger = logging.getLogger(__name__)
router = APIRouter()


def _run_ingestion():
    """Full ingestion pipeline: Drive → chunk → embed → upsert."""
    logger.info("Ingestion started.")
    files = drive_service.list_files()
    total_chunks = 0

    for file_meta in files:
        try:
            text = drive_service.download_file(file_meta)
            if not text.strip():
                logger.warning("Skipping empty file: %s", file_meta["name"])
                continue
            chunks = chunking_service.split(text, file_meta)
            vectors = embedding_service.embed_chunks(chunks)
            vectorstore_service.upsert(vectors)
            total_chunks += len(chunks)
            logger.info("Ingested '%s' → %d chunks", file_meta["name"], len(chunks))
        except Exception as exc:
            # Per rules.md: skip bad files, never crash the whole run
            logger.error("Failed to ingest '%s': %s", file_meta.get("name", "?"), exc)

    logger.info("Ingestion complete. Total chunks upserted: %d", total_chunks)


@router.post("/ingest", response_model=IngestResponse, tags=["ingest"])
async def ingest(background_tasks: BackgroundTasks):
    """
    Trigger Drive ingestion in the background.
    Returns immediately — check logs for progress.
    """
    try:
        background_tasks.add_task(_run_ingestion)
        return IngestResponse(
            status="started",
            message="Ingestion running in background. Check logs for progress.",
        )
    except Exception as exc:
        logger.exception("Failed to start ingestion: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to start ingestion.")
