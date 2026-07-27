"""
ingest_drive.py — Standalone CLI script to run the full ingestion pipeline.
Usage: python scripts/ingest_drive.py

Equivalent to hitting POST /ingest but runs inline so you can see all logs.
"""
import sys
import os
import logging

# Make sure the project root is on the path when running as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.logging import setup_logging
from app.services import drive_service, chunking_service, embedding_service, vectorstore_service

setup_logging()
logger = logging.getLogger(__name__)


def main():
    logger.info("=== Drive Ingestion CLI ===")

    # Ensure collection exists
    vectorstore_service.ensure_collection()

    files = drive_service.list_files()
    if not files:
        logger.warning("No supported files found in the Drive folder. Check GOOGLE_DRIVE_FOLDER_ID.")
        return

    logger.info("Found %d files to ingest.", len(files))
    total_chunks = 0

    for file_meta in files:
        logger.info("Processing: %s", file_meta["name"])
        text = drive_service.download_file(file_meta)

        if not text.strip():
            logger.warning("  Skipped (empty text): %s", file_meta["name"])
            continue

        chunks = chunking_service.split(text, file_meta)
        logger.info("  Chunks: %d", len(chunks))

        vectors = embedding_service.embed_chunks(chunks)
        vectorstore_service.upsert(vectors)
        total_chunks += len(chunks)
        logger.info("  Upserted to Qdrant [OK]")

    logger.info("=== Done. Total chunks upserted: %d ===", total_chunks)


if __name__ == "__main__":
    main()
