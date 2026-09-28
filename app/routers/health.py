from fastapi import APIRouter

from app.config import GROQ_API_KEY
from app.services.vector_store import get_qdrant_client

router = APIRouter()


def _check_qdrant() -> str:
    try:
        get_qdrant_client().get_collections()
        return "up"
    except Exception:
        return "down"


@router.get("/health")
def health_check():
    return {
        "api": "up",
        "qdrant": _check_qdrant(),
        "groq": "configured" if GROQ_API_KEY else "missing_api_key",
    }