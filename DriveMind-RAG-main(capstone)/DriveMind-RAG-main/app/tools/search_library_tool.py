"""
search_library_tool.py — Tool definition + handler for the Gemini agent.
The agent calls search_library(query, top_k) to retrieve context from Qdrant.
This file is the only place the tool schema lives — per rules.md, no duplication.
"""
import logging
from typing import Any, Dict, List

import google.generativeai as genai

from app.services import vectorstore_service

logger = logging.getLogger(__name__)

# ── Tool schema (Gemini function declaration format) ─────────────────────────

SEARCH_LIBRARY_TOOL = genai.protos.Tool(
    function_declarations=[
        genai.protos.FunctionDeclaration(
            name="search_library",
            description=(
                "Search the user's personal document library for chunks of text "
                "relevant to the query. Always call this tool before answering "
                "library-specific questions. Returns relevant text excerpts with "
                "source file names and links."
            ),
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "query": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="The search query to find relevant library content.",
                    ),
                    "top_k": genai.protos.Schema(
                        type=genai.protos.Type.INTEGER,
                        description="Number of chunks to retrieve (default 6, max 8).",
                    ),
                },
                required=["query"],
            ),
        )
    ]
)


# ── Tool handler ─────────────────────────────────────────────────────────────

def handle_search_library(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the search_library tool call.
    Called by agent_service when Gemini requests this function.
    Returns a dict that will be sent back to Gemini as the function result.
    """
    query: str = args.get("query", "")
    top_k: int = min(int(args.get("top_k", 6)), 8)  # cap at 8 per rules.md

    logger.info("Tool call: search_library(query='%s', top_k=%d)", query[:80], top_k)

    try:
        results = vectorstore_service.search(query, top_k=top_k)
    except Exception as exc:
        logger.error("search_library failed: %s", exc)
        return {"error": str(exc), "chunks": []}

    # Format for Gemini — return a clean structure it can read easily
    chunks = [
        {
            "text": r["text"],
            "source_file": r["source_file"],
            "drive_link": r.get("drive_link", ""),
            "chunk_index": r.get("chunk_index"),
            "relevance_score": round(r.get("score", 0), 4),
        }
        for r in results
    ]

    logger.info("search_library returned %d chunks.", len(chunks))
    return {"chunks": chunks}
