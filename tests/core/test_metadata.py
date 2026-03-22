"""Tests for metadata models."""

from datetime import UTC
from datetime import datetime

from media_downloader.core.metadata import InstagramMetadata
from media_downloader.core.metadata import WebRecipeMetadata
from media_downloader.core.metadata import YtDlpMetadata


def test_instagram_metadata_defaults() -> None:
    """InstagramMetadata has expected defaults."""
    meta = InstagramMetadata(shortcode="abc123")
    assert meta.shortcode == "abc123"
    assert meta.owner_username == ""
    assert meta.timestamp is None
    assert meta.like_count == 0
    assert meta.is_video is False


def test_instagram_metadata_full() -> None:
    """InstagramMetadata accepts all fields."""
    ts = datetime(2024, 1, 1, tzinfo=UTC)
    meta = InstagramMetadata(
        shortcode="abc123",
        owner_username="testuser",
        timestamp=ts,
        like_count=42,
        is_video=True,
    )
    assert meta.owner_username == "testuser"
    assert meta.like_count == 42


def test_ytdlp_metadata_defaults() -> None:
    """YtDlpMetadata has expected defaults."""
    meta = YtDlpMetadata(extractor="youtube")
    assert meta.extractor == "youtube"
    assert meta.title == ""
    assert meta.duration == 0.0


def test_web_recipe_metadata_defaults() -> None:
    """WebRecipeMetadata has expected defaults."""
    meta = WebRecipeMetadata()
    assert meta.recipe_title == ""
    assert meta.host == ""
    assert meta.ingredients is None
