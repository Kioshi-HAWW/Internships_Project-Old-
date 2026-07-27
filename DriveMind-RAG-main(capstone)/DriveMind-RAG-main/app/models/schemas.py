"""
schemas.py — Pydantic request/response models (single source of truth for API shapes).
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional


# ── /chat ────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="User question")


class SourceChunk(BaseModel):
    source_file: str
    drive_link: Optional[str] = None
    chunk_index: int
    page: Optional[int] = None
    text_snippet: str  # first ~200 chars for UI preview


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk] = []


# ── /ingest ───────────────────────────────────────────────────────────────────

class IngestResponse(BaseModel):
    status: str   # "started" | "error"
    message: str
