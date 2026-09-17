import datetime
import uuid

from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    file_id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    project_name = Column(
        String,
        nullable=False,
        default="unknown-project"
    )

    zip_file_name = Column(
        String,
        nullable=False,
        default="unknown.zip"
    )

    project_folder = Column(
        String,
        nullable=False,
        default=""
    )

    file_path = Column(
        String,
        nullable=False
    )

    file_extension = Column(
        String,
        nullable=False
    )

    total_chunks = Column(
        Integer,
        default=0
    )

    indexed_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )

    status = Column(
        String,
        default="pending"
    )


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()