"""
drive_service.py — Google Drive integration.
Uses a Service Account (not OAuth) as decided in rules.md.
Supports: pdf, docx, Google Docs (exported as text), txt, md.
"""
import io
import logging
from typing import List, Dict, Any

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import pypdf
import docx

from app.core.config import settings

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# MIME type → handler key
SUPPORTED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.google-apps.document": "gdoc",
    "text/plain": "txt",
    "text/markdown": "txt",
}


def _get_drive_service():
    """Build and return an authenticated Drive API client."""
    creds_info = settings.get_service_account_info()
    creds = service_account.Credentials.from_service_account_info(
        creds_info, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def list_files() -> List[Dict[str, Any]]:
    """
    List all supported files inside the configured Drive folder.
    Returns a list of dicts: {id, name, mimeType, webViewLink}.
    """
    service = _get_drive_service()
    folder_id = settings.google_drive_folder_id

    mime_filter = " or ".join(
        f"mimeType='{m}'" for m in SUPPORTED_MIME_TYPES
    )
    query = f"'{folder_id}' in parents and ({mime_filter}) and trashed=false"

    results = []
    page_token = None

    while True:
        resp = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, webViewLink)",
            pageToken=page_token,
        ).execute()

        results.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    logger.info("Found %d supported files in Drive folder %s", len(results), folder_id)
    return results


def download_file(file_meta: Dict[str, Any]) -> str:
    """
    Download/export a Drive file and return its text content.
    Skips and returns '' on any error (per rules.md error handling).
    """
    service = _get_drive_service()
    file_id = file_meta["id"]
    mime = file_meta["mimeType"]
    name = file_meta["name"]

    try:
        if mime == "application/vnd.google-apps.document":
            # Export Google Doc as plain text
            resp = service.files().export(fileId=file_id, mimeType="text/plain").execute()
            return resp.decode("utf-8") if isinstance(resp, bytes) else resp

        # Binary download for pdf / docx / txt
        request = service.files().get_media(fileId=file_id)
        buf = io.BytesIO()
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        buf.seek(0)

        handler = SUPPORTED_MIME_TYPES.get(mime, "txt")

        if handler == "pdf":
            return _extract_pdf(buf, name)
        if handler == "docx":
            return _extract_docx(buf, name)
        # txt / md
        return buf.read().decode("utf-8", errors="replace")

    except Exception as exc:
        logger.error("Failed to download '%s' (%s): %s", name, file_id, exc)
        return ""


# ── Private helpers ───────────────────────────────────────────────────────────

def _extract_pdf(buf: io.BytesIO, name: str) -> str:
    try:
        reader = pypdf.PdfReader(buf)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    except Exception as exc:
        logger.error("PDF extraction failed for '%s': %s", name, exc)
        return ""


def _extract_docx(buf: io.BytesIO, name: str) -> str:
    try:
        doc = docx.Document(buf)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as exc:
        logger.error("DOCX extraction failed for '%s': %s", name, exc)
        return ""
