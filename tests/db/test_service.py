"""Tests for DownloadDBService."""

from pathlib import Path

import pytest
import pytest_asyncio

from media_downloader.core.models import DownloadedMedia
from media_downloader.core.models import SourceType
from media_downloader.db.service import DownloadDBService


@pytest_asyncio.fixture
async def db_service(tmp_path: Path) -> DownloadDBService:
    """Create an initialized DB service for tests."""
    db = DownloadDBService(db_path=tmp_path / "test.db")
    await db.init_db()
    return db


@pytest.mark.asyncio
async def test_create_job(db_service: DownloadDBService) -> None:
    """Create a pending download job."""
    job = await db_service.create_job("https://youtube.com/watch?v=abc")
    assert job.id
    assert job.url == "https://youtube.com/watch?v=abc"
    assert job.status == "pending"


@pytest.mark.asyncio
async def test_get_job(db_service: DownloadDBService) -> None:
    """Fetch a job by ID."""
    job = await db_service.create_job("https://youtube.com/watch?v=abc")
    fetched = await db_service.get_job(job.id)
    assert fetched is not None
    assert fetched.id == job.id


@pytest.mark.asyncio
async def test_get_job_not_found(db_service: DownloadDBService) -> None:
    """Return None for non-existent job."""
    assert await db_service.get_job("nonexistent") is None


@pytest.mark.asyncio
async def test_get_pending_jobs(db_service: DownloadDBService) -> None:
    """Fetch pending jobs in creation order."""
    await db_service.create_job("https://a.com")
    await db_service.create_job("https://b.com")
    pending = await db_service.get_pending_jobs()
    assert len(pending) == 2
    assert pending[0].url == "https://a.com"


@pytest.mark.asyncio
async def test_mark_running(db_service: DownloadDBService) -> None:
    """Mark a job as running."""
    job = await db_service.create_job("https://a.com")
    await db_service.mark_running(job.id)
    updated = await db_service.get_job(job.id)
    assert updated is not None
    assert updated.status == "running"


@pytest.mark.asyncio
async def test_mark_completed(
    db_service: DownloadDBService,
    tmp_path: Path,
) -> None:
    """Mark a job as completed with download results."""
    job = await db_service.create_job("https://a.com")

    video_fp = tmp_path / "video.mp4"
    video_fp.touch()
    media = DownloadedMedia(
        source=SourceType.YOUTUBE,
        source_id="vid1",
        original_url="https://a.com",
        video_file=video_fp,
        all_files=[video_fp],
        caption="Test video",
    )

    await db_service.mark_completed(job.id, media)
    updated = await db_service.get_job(job.id)
    assert updated is not None
    assert updated.status == "completed"
    assert updated.source == "youtube"
    assert updated.source_id == "vid1"


@pytest.mark.asyncio
async def test_mark_failed(db_service: DownloadDBService) -> None:
    """Mark a job as failed with error."""
    job = await db_service.create_job("https://a.com")
    await db_service.mark_failed(job.id, "Download timeout")
    updated = await db_service.get_job(job.id)
    assert updated is not None
    assert updated.status == "failed"
    assert updated.error == "Download timeout"
