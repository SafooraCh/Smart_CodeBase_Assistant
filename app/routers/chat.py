from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import SEARCH_TOP_K, SEARCH_SCORE_THRESHOLD
from app.services.vector_store import search_chunks
from app.services.llm_client import generate_answer


router = APIRouter()

FALLBACK_MESSAGE = (
    "I could not find relevant code or documentation matching your request "
    "in the indexed files."
)

_NOT_FOUND_PHRASES = [
    "not enough information",
    "does not contain",
    "doesn't contain",
    "does not mention",
    "doesn't mention",
    "cannot find",
    "can't find",
    "could not find",
    "couldn't find",
    "no information",
    "not found",
    "i don't see",
    "i do not see",
]


def _llm_says_not_found(answer_text: str) -> bool:
    lowered = answer_text.lower()
    return any(phrase in lowered for phrase in _NOT_FOUND_PHRASES)


class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Natural language developer question",
    )
    project_name: str | None = Field(
        default=None,
        description=(
            "If set, the model will only be given context from this "
            "indexed project. Use GET /codebase/projects to see available "
            "names."
        ),
    )


class Citation(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    score: float


class ChatResponse(BaseModel):
    query: str
    answer: str
    citations: list[Citation]
    grounded: bool


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    chunks = search_chunks(
        query=request.query,
        top_k=SEARCH_TOP_K,
        score_threshold=SEARCH_SCORE_THRESHOLD,
        project_name=request.project_name,
    )

    if not chunks:
        fallback = FALLBACK_MESSAGE
        if request.project_name:
            fallback = (
                f"I could not find relevant code or documentation for "
                f"project '{request.project_name}' matching your request."
            )

        return ChatResponse(
            query=request.query,
            answer=fallback,
            citations=[],
            grounded=False,
        )

    try:
        answer_text = generate_answer(
            query=request.query,
            context_chunks=chunks,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Local LLM (Ollama) call failed: {exc}. "
                "Check that Ollama is running and the model is pulled."
            ),
        )


    if _llm_says_not_found(answer_text):
        return ChatResponse(
            query=request.query,
            answer=FALLBACK_MESSAGE,
            citations=[],
            grounded=False,
        )

    citations = [
        Citation(
            file_path=c["file_path"],
            start_line=c["start_line"],
            end_line=c["end_line"],
            score=c["score"],
        )
        for c in chunks
    ]

    return ChatResponse(
        query=request.query,
        answer=answer_text,
        citations=citations,
        grounded=True,
    )