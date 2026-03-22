"""Tests for DownloadedMedia model."""

from media_downloader.core.models import DownloadedMedia
from media_downloader.core.models import JobStatus
from media_downloader.core.models import SourceType


def test_source_type_values() -> None:
    """Source type enum has expected values."""
    assert SourceType.INSTAGRAM.value == "instagram"
    assert SourceType.YOUTUBE.value == "youtube"
    assert SourceType.TIKTOK.value == "tiktok"
    assert SourceType.WEB_RECIPE.value == "web_recipe"
    assert SourceType.UNKNOWN.value == "unknown"


def test_job_status_values() -> None:
    """Job status enum has expected values."""
    assert JobStatus.PENDING.value == "pending"
    assert JobStatus.RUNNING.value == "running"
    assert JobStatus.COMPLETED.value == "completed"
    assert JobStatus.FAILED.value == "failed"


def test_downloaded_media_defaults() -> None:
    """DownloadedMedia has sensible defaults."""
    media = DownloadedMedia(
        source=SourceType.YOUTUBE,
        source_id="abc123",
        original_url="https://youtube.com/watch?v=abc123",
    )
    assert media.video_file is None
    assert media.audio_file is None
    assert media.thumbnail_file is None
    assert media.all_files == []
    assert media.caption == ""
    assert media.transcription is None
    assert media.metadata is None


def test_downloaded_media_language_property_none() -> None:
    """Language property returns None when no transcription."""
    media = DownloadedMedia(
        source=SourceType.YOUTUBE,
        source_id="abc123",
        original_url="https://youtube.com/watch?v=abc123",
    )
    assert media.language is None


def test_downloaded_media_transcript_property_none() -> None:
    """Transcript property returns None when no transcription."""
    media = DownloadedMedia(
        source=SourceType.YOUTUBE,
        source_id="abc123",
        original_url="https://youtube.com/watch?v=abc123",
    )
    assert media.transcript is None
