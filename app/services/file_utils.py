import zipfile
from pathlib import Path

from app.config import (
    ALLOWED_EXTENSIONS,
    IGNORED_DIR_NAMES,
    IGNORED_FILE_PATTERNS,
    MAX_UNCOMPRESSED_SIZE_BYTES,
    MAX_COMPRESSION_RATIO,
)


class InvalidZipError(ValueError):
    """Raised when the uploaded file is not a usable zip archive."""


def extract_zip(zip_path: str, extract_to: str) -> str:
    extract_to_path = Path(extract_to).resolve()

    if not zipfile.is_zipfile(zip_path):
        raise InvalidZipError(
            "The uploaded file is not a valid zip archive "
            "(it may be corrupted or a different file type)."
        )

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            bad_file = zf.testzip()
            if bad_file is not None:
                raise InvalidZipError(
                    f"The zip archive is corrupted (bad file: {bad_file})."
                )

            infos = zf.infolist()

            
            if not infos:
                raise InvalidZipError("The zip archive is empty.")

            total_uncompressed = 0

            for member in infos:
                member_path = (extract_to_path / member.filename).resolve()

                
                if not str(member_path).startswith(str(extract_to_path)):
                    raise InvalidZipError(f"Unsafe path in zip: {member.filename}")

                total_uncompressed += member.file_size
                if total_uncompressed > MAX_UNCOMPRESSED_SIZE_BYTES:
                    raise InvalidZipError(
                        "The zip archive is too large when extracted "
                        f"(limit is {MAX_UNCOMPRESSED_SIZE_BYTES // (1024 * 1024)} MB)."
                    )

                if member.compress_size > 0:
                    ratio = member.file_size / member.compress_size
                    if ratio > MAX_COMPRESSION_RATIO:
                        raise InvalidZipError(
                            f"Suspicious compression ratio in zip entry "
                            f"'{member.filename}' (possible zip bomb)."
                        )

            try:
                zf.extractall(extract_to_path)
            except RuntimeError as exc:
                
                raise InvalidZipError(
                    "The zip archive appears to be password-protected, "
                    "which is not supported."
                ) from exc

    except zipfile.BadZipFile as exc:
        raise InvalidZipError(
            "The zip archive is corrupted and could not be read."
        ) from exc

    return str(extract_to_path)


def is_ignored(path: Path) -> bool:
    if any(part in IGNORED_DIR_NAMES for part in path.parts):
        return True

    if any(
        str(path).endswith(pattern)
        for pattern in IGNORED_FILE_PATTERNS
    ):
        return True

    return False


def collect_valid_files(root_dir: str) -> list[Path]:
    root = Path(root_dir)
    valid_files = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if is_ignored(path.relative_to(root)):
            continue

        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        if path.stat().st_size == 0:
            continue

        valid_files.append(path)

    return valid_files