"""
health.py — GET /health
Simple liveness check for Render and monitoring tools.
"""
from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check():
    """Returns 200 OK if the service is alive."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
