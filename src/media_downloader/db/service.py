"""Download database service.

``DownloadDBService`` provides async CRUD operations for download jobs
and their associated media files. Uses SQLAlchemy async with aiosqlite.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from loguru import logger as lg
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import selectinload

from media_downloader.db.models import Base
from media_downloader.db.models import DownloadJob
from media_downloader.db.models import MediaFile

if TYPE_CHECKING:
    from pathlib import Path

    from media_downloader.core.models import DownloadedMedia


class DownloadDBService:
    """Async database service for download job management.

    Attributes:
        db_path:
            Path to the SQLite database file.
    """

    def __init__(self, db_path: Path) -> None:
        """Initialize with the database file path.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_async_engine(
            f"sqlite+aiosqlite:///{db_path}",
            echo=False,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
        )

    async def init_db(self) -> None:
        """Create tables and enable WAL mode for concurrent access."""
        async with self._engine.begin() as conn:
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.run_sync(Base.metadata.create_all)
        lg.info(f"Database initialized: {self.db_path}")

    async def create_job(self, url: str) -> DownloadJob:
        """Create a new pending download job.

        Args:
            url: The URL to download.

        Returns:
            The new ``DownloadJob`` with status ``"pending"``.
        """
        job = DownloadJob(
            id=uuid.uuid4().hex,
            url=url,
            status="pending",
        )
        async with self._session_factory() as session:
            session.add(job)
            await session.commit()
        lg.info(f"Created job {job.id} for {url}")
        return job

    async def get_job(self, job_id: str) -> DownloadJob | None:
        """Fetch a job by ID.

        Args:
            job_id: The job identifier.

        Returns:
            The job, or None if not found.
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(DownloadJob)
                .where(DownloadJob.id == job_id)
                .options(selectinload(DownloadJob.media_files))
            )
            return result.scalar_one_or_none()

    async def get_pending_jobs(self) -> list[DownloadJob]:
        """Fetch all pending jobs ordered by creation time.

        Returns:
            List of pending ``DownloadJob`` instances.
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(DownloadJob)
                .where(DownloadJob.status == "pending")
                .order_by(DownloadJob.created_at),
            )
            return list(result.scalars().all())

    async def mark_running(self, job_id: str) -> None:
        """Mark a job as running.

        Args:
            job_id: The job identifier.
        """
        await self._update_status(job_id, "running")

    async def mark_completed(
        self,
        job_id: str,
        media: DownloadedMedia,
    ) -> None:
        """Mark a job as completed and persist download results.

        Args:
            job_id: The job identifier.
            media: The completed download result.
        """
        async with self._session_factory() as session:
            job = await session.get(DownloadJob, job_id)
            if job is None:
                lg.warning(f"Job {job_id} not found for completion")
                return

            job.status = "completed"
            job.source = media.source.value
            job.source_id = media.source_id
            job.transcript = media.transcript
            job.language = media.language

            # Add media file records
            for fp in media.all_files:
                role = _infer_role(fp)
                mf = MediaFile(
                    job_id=job_id,
                    file_path=str(fp),
                    role=role,
                    media_on_disk=True,
                )
                session.add(mf)

            await session.commit()
        lg.info(f"Job {job_id} completed: {media.source.value}/{media.source_id}")

    async def mark_failed(self, job_id: str, error: str) -> None:
        """Mark a job as failed with an error message.

        Args:
            job_id: The job identifier.
            error: Error description.
        """
        async with self._session_factory() as session:
            job = await session.get(DownloadJob, job_id)
            if job is None:
                lg.warning(f"Job {job_id} not found for failure marking")
                return
            job.status = "failed"
            job.error = error
            await session.commit()
        lg.warning(f"Job {job_id} failed: {error}")

    async def _update_status(self, job_id: str, status: str) -> None:
        """Update a job's status field.

        Args:
            job_id: The job identifier.
            status: New status value.
        """
        async with self._session_factory() as session:
            job = await session.get(DownloadJob, job_id)
            if job is None:
                return
            job.status = status
            await session.commit()

    async def close(self) -> None:
        """Dispose of the database engine."""
        await self._engine.dispose()


def _infer_role(fp: Path) -> str:
    """Infer a media file's role from its name or extension.

    Args:
        fp: Path to the media file.

    Returns:
        Role string (``"video"``, ``"audio"``, ``"thumbnail"``, ``"recipe"``,
        or ``"unknown"``).
    """
    stem = fp.stem.lower()
    suffix = fp.suffix.lower()

    if stem == "audio" or suffix in {".wav", ".mp3", ".m4a", ".aac", ".flac"}:
        return "audio"
    if stem == "video" or suffix in {".mp4", ".webm", ".mkv"}:
        return "video"
    if stem == "thumbnail" or suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        return "thumbnail"
    if stem == "recipe" or suffix == ".txt":
        return "recipe"
    return "unknown"
