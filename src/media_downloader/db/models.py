"""SQLAlchemy ORM models for download job tracking.

Defines the ``DownloadJob`` and ``MediaFile`` tables that persist download
state and file references to the SQLite database.
"""

from __future__ import annotations

from datetime import UTC
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for download tracking."""


class DownloadJob(Base):
    """A single download request and its lifecycle state.

    Attributes:
        id:
            Primary key, typically a UUID string.
        url:
            Original URL submitted for download.
        source:
            Detected source type value (e.g. ``"instagram"``).
        source_id:
            Platform-specific content identifier.
        status:
            Job lifecycle state (pending, running, completed, failed).
        error:
            Error message if the job failed, else None.
        transcript:
            Transcribed text, if transcription was performed.
        language:
            Detected language from transcription.
        created_at:
            When the job was created.
        updated_at:
            When the job was last updated.
        media_files:
            Related ``MediaFile`` rows.
    """

    __tablename__ = "download_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    source_id: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    media_files: Mapped[list[MediaFile]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )


class MediaFile(Base):
    """A single media file belonging to a download job.

    Attributes:
        id:
            Auto-incremented primary key.
        job_id:
            Foreign key to ``DownloadJob.id``.
        file_path:
            Relative path from the media base directory.
        role:
            File role (``"video"``, ``"thumbnail"``, ``"audio"``, etc.).
        media_on_disk:
            Whether the file currently exists on disk.
        job:
            Parent ``DownloadJob``.
    """

    __tablename__ = "media_files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("download_jobs.id"),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    media_on_disk: Mapped[bool] = mapped_column(default=True)

    job: Mapped[DownloadJob] = relationship(back_populates="media_files")
