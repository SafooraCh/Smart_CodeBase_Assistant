import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION
from app.services.embedder import EMBEDDING_DIM, embed_texts


_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    global _client

    if _client is None:
        _client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT
        )

    return _client


def ensure_collection():
    client = get_qdrant_client()

    existing = [
        c.name
        for c in client.get_collections().collections
    ]

    if QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=qmodels.VectorParams(
                size=EMBEDDING_DIM,
                distance=qmodels.Distance.COSINE
            ),
        )


def store_chunks(
    file_id: str,
    file_path: str,
    chunks: list[dict],
    project_name: str = "unknown-project",
    zip_file_name: str = "unknown.zip",
) -> int:
    """
    Creates embeddings and stores chunks in Qdrant
    using small batches to avoid large request errors.
    """

    if not chunks:
        return 0

    ensure_collection()

    client = get_qdrant_client()

    BATCH_SIZE = 50
    total_stored = 0

    for i in range(0, len(chunks), BATCH_SIZE):

        batch = chunks[i:i + BATCH_SIZE]

        texts = [
            chunk["text"]
            for chunk in batch
        ]

        vectors = embed_texts(texts)

        points = [
            qmodels.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "file_id": file_id,
                    "project_name": project_name,
                    "zip_file_name": zip_file_name,
                    "file_path": file_path,
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "text": chunk["text"],
                },
            )
            for chunk, vector in zip(batch, vectors)
        ]

        client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=points
        )

        total_stored += len(points)

    return total_stored


def get_chunks_by_file_id(file_id: str) -> list[dict]:
    client = get_qdrant_client()

    ensure_collection()

    points, _ = client.scroll(
        collection_name=QDRANT_COLLECTION,
        scroll_filter=qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="file_id",
                    match=qmodels.MatchValue(value=file_id)
                )
            ]
        ),
        limit=1000,
        with_payload=True,
        with_vectors=False,
    )

    chunks = [
        {
            "chunk_point_id": point.id,
            "project_name": point.payload.get("project_name"),
            "zip_file_name": point.payload.get("zip_file_name"),
            "file_path": point.payload.get("file_path"),
            "start_line": point.payload.get("start_line"),
            "end_line": point.payload.get("end_line"),
            "text": point.payload.get("text"),
        }
        for point in points
    ]

    chunks.sort(
        key=lambda c: (
            c["start_line"] is None,
            c["start_line"]
        )
    )

    return chunks


def get_full_text_by_file_id(file_id: str) -> str:
    """Reconstruct the full readable text of a file from its ordered chunks."""

    chunks = get_chunks_by_file_id(file_id)

    return "\n".join(
        chunk["text"]
        for chunk in chunks
    )


def search_chunks(
    query: str,
    top_k: int,
    score_threshold: float
) -> list[dict]:

    ensure_collection()

    client = get_qdrant_client()

    query_vector = embed_texts([query])[0]

    results = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=top_k,
        score_threshold=score_threshold,
        with_payload=True,
    )

    return [
        {
            "project_name": r.payload.get("project_name"),
            "zip_file_name": r.payload.get("zip_file_name"),
            "file_path": r.payload.get("file_path"),
            "start_line": r.payload.get("start_line"),
            "end_line": r.payload.get("end_line"),
            "text": r.payload.get("text"),
            "score": round(r.score, 4),
        }
        for r in results
    ]
def search_chunks(
    query: str,
    top_k: int,
    score_threshold: float,
    project_name: str | None = None,
) -> list[dict]:

    ensure_collection()

    client = get_qdrant_client()

    query_vector = embed_texts([query])[0]

    query_filter = None

    if project_name:
        query_filter = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="project_name",
                    match=qmodels.MatchValue(value=project_name),
                )
            ]
        )

    results = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vector,
        query_filter=query_filter,
        limit=top_k,
        score_threshold=score_threshold,
        with_payload=True,
    )

    return [
        {
            "project_name": r.payload.get("project_name"),
            "zip_file_name": r.payload.get("zip_file_name"),
            "file_path": r.payload.get("file_path"),
            "start_line": r.payload.get("start_line"),
            "end_line": r.payload.get("end_line"),
            "text": r.payload.get("text"),
            "score": round(r.score, 4),
        }
        for r in results
    ]

def delete_chunks_by_file_id(file_id: str) -> None:
    client = get_qdrant_client()

    ensure_collection()

    client.delete(
        collection_name=QDRANT_COLLECTION,
        points_selector=qmodels.FilterSelector(
            filter=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="file_id",
                        match=qmodels.MatchValue(value=file_id)
                    )
                ]
            )
        ),
    )