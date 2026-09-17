from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config import SEARCH_TOP_K, SEARCH_SCORE_THRESHOLD
from app.services.vector_store import search_chunks


router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Natural language question or keywords",
    )
    project_name: str | None = Field(
        default=None,
        description=(
            "If set, restrict results to chunks from this indexed project "
            "only. Use GET /codebase/projects to see available names."
        ),
    )


class SearchResultChunk(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    text: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results_found: int
    results: list[SearchResultChunk]
    message: str | None = None


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    results = search_chunks(
        query=request.query,
        top_k=SEARCH_TOP_K,
        score_threshold=SEARCH_SCORE_THRESHOLD,
        project_name=request.project_name,
    )

    message = None

    if not results:
        message = (
            "I could not find relevant code or documentation matching "
            "your request in the indexed files."
        )

    return SearchResponse(
        query=request.query,
        results_found=len(results),
        results=results,
        message=message,
    )