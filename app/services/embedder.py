from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL_NAME

EMBEDDING_DIM = 384


@lru_cache(maxsize=1)
def get_embedder() -> SentenceTransformer:
    """Loads the model once and caches it."""
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_texts(
    texts: list[str],
    batch_size: int = 32
) -> list[list[float]]:
    """
    Takes chunk texts and creates embeddings in small batches.
    Returns vectors in the same order as the input texts.
    """

    if not texts:
        return []

    model = get_embedder()

    vectors = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True
    )

    return vectors.tolist()