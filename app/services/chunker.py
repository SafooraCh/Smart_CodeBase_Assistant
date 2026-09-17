from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

EXTENSION_LANGUAGE_MAP = {
    ".py": Language.PYTHON,
    ".js": Language.JS,
    ".ts": Language.TS,
    ".md": Language.MARKDOWN,
}

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def get_splitter(extension: str) -> RecursiveCharacterTextSplitter:
    language = EXTENSION_LANGUAGE_MAP.get(extension.lower())

    if language:
        return RecursiveCharacterTextSplitter.from_language(
            language=language,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )


def chunk_file(file_path: Path, relative_path: str) -> list[dict]:
    text = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    if not text.strip():
        return []

    splitter = get_splitter(file_path.suffix)
    raw_chunks = splitter.split_text(text)

    chunks = []
    search_from = 0

    for raw_chunk in raw_chunks:
        start_char = text.find(raw_chunk, search_from)

        if start_char == -1:
            start_char = text.find(raw_chunk)

        end_char = start_char + len(raw_chunk)
        search_from = start_char + 1

        start_line = text.count("\n", 0, start_char) + 1
        end_line = text.count("\n", 0, end_char) + 1

        chunks.append({
            "text": raw_chunk,
            "file_path": relative_path,
            "start_line": start_line,
            "end_line": end_line,
        })

    return chunks