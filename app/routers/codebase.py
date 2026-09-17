import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR
from app.database import get_db, FileMetadata
from app.services.file_utils import extract_zip, collect_valid_files, InvalidZipError
from app.services.chunker import chunk_file
from app.services.vector_store import (
    store_chunks,
    get_chunks_by_file_id,
    get_full_text_by_file_id,
    delete_chunks_by_file_id,
)

router = APIRouter()


@router.post("/codebase/index")
async def index_codebase(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only .zip files are supported. Please upload a zip archive.",
        )

    job_id = str(uuid.uuid4())

    zip_file_name = Path(file.filename).name
    project_name = Path(zip_file_name).stem

    job_dir = Path(UPLOAD_DIR) / project_name / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    zip_path = job_dir / file.filename

    with open(zip_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        extracted_root = extract_zip(str(zip_path), str(job_dir / "extracted"))
    except InvalidZipError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    valid_files = collect_valid_files(extracted_root)

    if not valid_files:
        return {
            "job_id": job_id,
            "files_processed": 0,
            "files": [],
            "message": (
                "No supported files were found in this zip "
                f"(supported types: .py, .js, .ts, .md, .json, .yaml, .yml, .txt)."
            ),
        }

    results = []

    for path in valid_files:
        relative_path = str(path.relative_to(extracted_root))
        chunks = chunk_file(path, relative_path)

        record = FileMetadata(
    project_name=project_name,
    zip_file_name=zip_file_name,
    project_folder=str(job_dir / "extracted"),
    file_path=relative_path,
    file_extension=path.suffix.lower(),
    total_chunks=len(chunks),
    status="indexed" if chunks else "failed",
)

        db.add(record)
        db.flush()

        vectors_stored = 0

        if chunks:
            try:
                vectors_stored = store_chunks(
    record.file_id,
    relative_path,
    chunks,
    project_name=project_name,
    zip_file_name=zip_file_name,
)
            except Exception as exc:
                record.status = "failed"

                results.append({
                    "file_id": record.file_id,
                    "file_path": relative_path,
                    "chunks_created": len(chunks),
                    "status": record.status,
                    "error": f"embedding/storage failed: {exc}",
                })

                continue

        results.append({
            "file_id": record.file_id,
            "file_path": relative_path,
            "chunks_created": len(chunks),
            "vectors_stored": vectors_stored,
            "status": record.status,
        })

    db.commit()

    return {
        "job_id": job_id,
        "files_processed": len(results),
        "files": results,
    }

@router.get("/codebase/projects")
def list_projects(db: Session = Depends(get_db)):
    """List distinct indexed project names, so the client can offer a
    'which project should I answer about' selector."""
    rows = (
        db.query(
            FileMetadata.project_name,
            FileMetadata.zip_file_name,
        )
        .distinct()
        .all()
    )

    projects: dict[str, dict] = {}

    for project_name, zip_file_name in rows:
        entry = projects.setdefault(
            project_name,
            {"project_name": project_name, "zip_file_names": set(), "file_count": 0},
        )
        entry["zip_file_names"].add(zip_file_name)

    for project_name in projects:
        file_count = (
            db.query(FileMetadata)
            .filter(FileMetadata.project_name == project_name)
            .count()
        )
        projects[project_name]["file_count"] = file_count
        projects[project_name]["zip_file_names"] = sorted(
            projects[project_name]["zip_file_names"]
        )

    return list(projects.values())

@router.get("/codebase/files")
def list_files(db: Session = Depends(get_db)):
    files = db.query(FileMetadata).all()

    return [
        {
            "file_id": f.file_id,
            "project_name": f.project_name,
            "zip_file_name": f.zip_file_name,
            "file_path": f.file_path,
            "file_extension": f.file_extension,
            "total_chunks": f.total_chunks,
            "status": f.status,
            "indexed_at": f.indexed_at.isoformat(),
        }
        for f in files
    ]


@router.get("/codebase/files/{file_id}")
def get_file(file_id: str, db: Session = Depends(get_db)):
    record = (
        db.query(FileMetadata)
        .filter(FileMetadata.file_id == file_id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"No indexed file found with file_id '{file_id}'"
        )

    chunks = get_chunks_by_file_id(file_id)

    return {
        "file_id": record.file_id,
        "project_name": record.project_name,
        "zip_file_name": record.zip_file_name,
        "file_path": record.file_path,
        "file_extension": record.file_extension,
        "total_chunks": record.total_chunks,
        "status": record.status,
        "indexed_at": record.indexed_at.isoformat(),
        "chunks": chunks,
    }


@router.get("/codebase/files/{file_id}/text")
def get_file_full_text(file_id: str, db: Session = Depends(get_db)):
    """Read the complete, reconstructed text of a file by its id (all
    chunks joined back together in the correct order)."""
    record = (
        db.query(FileMetadata)
        .filter(FileMetadata.file_id == file_id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"No indexed file found with file_id '{file_id}'"
        )

    full_text = get_full_text_by_file_id(file_id)

    return {
        "file_id": record.file_id,
        "file_path": record.file_path,
        "full_text": full_text,
    }


@router.delete("/codebase/files/{file_id}")
def delete_file(file_id: str, db: Session = Depends(get_db)):
    record = (
        db.query(FileMetadata)
        .filter(FileMetadata.file_id == file_id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"No indexed file found with file_id '{file_id}'"
        )

    delete_chunks_by_file_id(file_id)

    db.delete(record)
    db.commit()

    return {
        "file_id": file_id,
        "file_path": record.file_path,
        "deleted": True,
    }