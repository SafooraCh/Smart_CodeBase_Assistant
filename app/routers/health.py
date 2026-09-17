import httpx
from fastapi import APIRouter

from app.config import QDRANT_HOST, QDRANT_PORT, OLLAMA_HOST

router = APIRouter()


def _check_qdrant() -> str:
    try:
        r = httpx.get(f"http://{QDRANT_HOST}:{QDRANT_PORT}/readyz", timeout=3)
        return "up" if r.status_code == 200 else "down"
    except Exception:
        return "down"


def _check_ollama() -> str:
    try:
        r = httpx.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        return "up" if r.status_code == 200 else "down"
    except Exception:
        return "down"


@router.get("/health")
def health_check():
    return {
        "api": "up",
        "qdrant": _check_qdrant(),
        "ollama": _check_ollama(),
    }
