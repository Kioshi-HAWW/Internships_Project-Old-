"""
chat.py — POST /chat
Receives a user question, runs the Gemini agent loop, returns answer + sources.
"""
import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services import agent_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
def chat(request: ChatRequest):
    """
    Run the RAG agent loop for a user question.
    Returns a grounded answer with source citations.
    """
    try:
        result = agent_service.answer(request.message)
        return ChatResponse(answer=result["answer"], sources=result["sources"])
    except Exception as exc:
        logger.exception("Error in /chat: %s", exc)
        raise HTTPException(status_code=500, detail="Internal agent error.")
