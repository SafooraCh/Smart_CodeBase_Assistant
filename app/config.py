import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/db/metadata.db"
)

QDRANT_HOST = os.getenv(
    "QDRANT_HOST",
    "qdrant"
)

QDRANT_PORT = int(
    os.getenv("QDRANT_PORT", 6333)
)

QDRANT_COLLECTION = os.getenv(
    "QDRANT_COLLECTION",
    "codebase_chunks"
)

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "all-MiniLM-L6-v2"
)

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://ollama:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3:8b"
)

UPLOAD_DIR = os.getenv(
    "UPLOAD_DIR",
    "./data/uploads"
)

ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
}

IGNORED_DIR_NAMES = {
    "node_modules",
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    "dist",
    "build",
    ".next",
}

IGNORED_FILE_PATTERNS = {
    ".lock",
    ".min.js",
    ".map",
}
SEARCH_TOP_K = int(os.getenv("SEARCH_TOP_K", 5))
SEARCH_SCORE_THRESHOLD = float(os.getenv("SEARCH_SCORE_THRESHOLD", 0.3))

MAX_UNCOMPRESSED_SIZE_BYTES = int(
    os.getenv("MAX_UNCOMPRESSED_SIZE_BYTES", 500 * 1024 * 1024)  # 500 MB
)
MAX_COMPRESSION_RATIO = int(os.getenv("MAX_COMPRESSION_RATIO", 100))