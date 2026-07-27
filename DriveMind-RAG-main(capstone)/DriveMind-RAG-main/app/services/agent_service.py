"""
agent_service.py — Hand-rolled Gemini tool-use loop (no LangChain agents).
Per rules.md: keep it simple, use the google-generativeai SDK directly.

Flow per request:
  1. User question → Gemini with search_library tool definition.
  2. Gemini calls search_library → we execute it → send result back.
  3. Gemini reads result → composes cited answer.
  4. We parse and return {answer, sources[]}.
"""
import logging
from typing import Any, Dict, List

import google.generativeai as genai

from app.core.config import settings
from app.tools.search_library_tool import SEARCH_LIBRARY_TOOL, handle_search_library

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a personal library assistant. Your only job is to answer questions using \
information retrieved from the user's document library via the search_library tool.

Rules:
- Always call search_library before answering any library-specific question.
- Base your answer ONLY on the retrieved chunks. Do not guess or hallucinate.
- If the retrieved context is not relevant or insufficient, say so clearly.
- Cite the source file for every fact you state, e.g. (Source: filename.pdf).
- Keep answers clear, well-structured, and concise.
"""


def _init_model() -> genai.GenerativeModel:
    genai.configure(api_key=settings.gemini_api_key)
    return genai.GenerativeModel(
        model_name=settings.gemini_model,
        system_instruction=SYSTEM_PROMPT,
        tools=[SEARCH_LIBRARY_TOOL],
    )


# ── Public interface ──────────────────────────────────────────────────────────

def answer(question: str) -> Dict[str, Any]:
    """
    Run the Gemini tool-use loop for `question`.
    Returns {"answer": str, "sources": list[SourceChunk-like dicts]}.
    """
    try:
        model = _init_model()
        chat = model.start_chat(enable_automatic_function_calling=False)

        # Step 1: Send user question
        response = chat.send_message(question)
    except Exception as exc:
        logger.exception("Gemini API error during initial chat message: %s", exc)
        err_str = str(exc)
        if "429" in err_str or "quota" in err_str.lower() or "ResourceExhausted" in err_str:
            return {
                "answer": "⚠️ The Gemini API rate limit or daily quota has been reached. Please wait a minute before sending another question.",
                "sources": [],
            }
        return {
            "answer": f"⚠️ Gemini API connection error: {err_str}",
            "sources": [],
        }

    collected_sources: List[Dict] = []

    # Step 2: Agentic loop — handle function calls until final text
    for _ in range(5):  # guard against infinite loops
        # Check if Gemini wants to call a function
        function_calls = [
            part.function_call
            for candidate in response.candidates
            for part in candidate.content.parts
            if part.function_call.name
        ]

        if not function_calls:
            break  # Final text response — exit loop

        # Execute all requested tool calls
        tool_responses = []
        for fc in function_calls:
            fn_name = fc.name
            fn_args = dict(fc.args)

            if fn_name == "search_library":
                result = handle_search_library(fn_args)
                # Collect unique sources from this tool call
                for chunk in result.get("chunks", []):
                    if chunk not in collected_sources:
                        collected_sources.append(chunk)
            else:
                logger.warning("Unknown tool called: %s", fn_name)
                result = {"error": f"Unknown tool: {fn_name}"}

            tool_responses.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=fn_name,
                        response=result,
                    )
                )
            )

        # Step 3: Send tool results back to Gemini
        response = chat.send_message(tool_responses)

    # Extract final text answer
    final_text = ""
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if hasattr(part, "text") and part.text:
                final_text += part.text

    if not final_text:
        final_text = "I could not generate an answer. Please try rephrasing your question."

    # Build sources list for the API response
    sources = [
        {
            "source_file": s.get("source_file", ""),
            "drive_link": s.get("drive_link", ""),
            "chunk_index": s.get("chunk_index", 0),
            "page": s.get("page"),
            "text_snippet": s.get("text", "")[:200],
        }
        for s in collected_sources
    ]

    return {"answer": final_text, "sources": sources}
