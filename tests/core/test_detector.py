"""Tests for UrlDetector."""

import pytest

from media_downloader.core.detector import UrlDetector
from media_downloader.core.models import SourceType


@pytest.fixture
def detector() -> UrlDetector:
    """Create a UrlDetector instance."""
    return UrlDetector()


class TestInstagramDetection:
    """Tests for Instagram URL detection."""

    def test_post_url(self, detector: UrlDetector) -> None:
        """Detect Instagram post URL."""
        result = detector.detect("https://www.instagram.com/p/CsEj0n9Kefd/")
        assert result.source == SourceType.INSTAGRAM
        assert result.source_id == "CsEj0n9Kefd"

    def test_reel_url(self, detector: UrlDetector) -> None:
        """Detect Instagram reel URL."""
        result = detector.detect("https://www.instagram.com/reel/CsEj0n9Kefd/")
        assert result.source == SourceType.INSTAGRAM
        assert result.source_id == "CsEj0n9Kefd"

    def test_tv_url(self, detector: UrlDetector) -> None:
        """Detect Instagram TV URL."""
        result = detector.detect("https://www.instagram.com/tv/CsEj0n9Kefd/")
        assert result.source == SourceType.INSTAGRAM
        assert result.source_id == "CsEj0n9Kefd"


class TestYouTubeDetection:
    """Tests for YouTube URL detection."""

    def test_watch_url(self, detector: UrlDetector) -> None:
        """Detect YouTube watch URL."""
        result = detector.detect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert result.source == SourceType.YOUTUBE
        assert result.source_id == "dQw4w9WgXcQ"

    def test_short_url(self, detector: UrlDetector) -> None:
        """Detect YouTube short URL."""
        result = detector.detect("https://youtu.be/dQw4w9WgXcQ")
        assert result.source == SourceType.YOUTUBE
        assert result.source_id == "dQw4w9WgXcQ"

    def test_shorts_url(self, detector: UrlDetector) -> None:
        """Detect YouTube Shorts URL."""
        result = detector.detect("https://www.youtube.com/shorts/dQw4w9WgXcQ")
        assert result.source == SourceType.YOUTUBE
        assert result.source_id == "dQw4w9WgXcQ"


class TestTikTokDetection:
    """Tests for TikTok URL detection."""

    def test_video_url(self, detector: UrlDetector) -> None:
        """Detect TikTok video URL."""
        result = detector.detect(
            "https://www.tiktok.com/@user/video/7234567890123456789",
        )
        assert result.source == SourceType.TIKTOK
        assert result.source_id == "7234567890123456789"


class TestWebRecipeDetection:
    """Tests for web recipe URL detection."""

    def test_allrecipes(self, detector: UrlDetector) -> None:
        """Detect allrecipes URL."""
        result = detector.detect("https://www.allrecipes.com/recipe/12345/pasta/")
        assert result.source == SourceType.WEB_RECIPE

    def test_seriouseats(self, detector: UrlDetector) -> None:
        """Detect Serious Eats URL."""
        result = detector.detect("https://www.seriouseats.com/best-pasta-recipe")
        assert result.source == SourceType.WEB_RECIPE


class TestUnknownDetection:
    """Tests for unknown URL detection."""

    def test_unknown_url(self, detector: UrlDetector) -> None:
        """Unknown URL returns UNKNOWN source type."""
        result = detector.detect("https://example.com/some-page")
        assert result.source == SourceType.UNKNOWN
        assert result.source_id == "https://example.com/some-page"

    def test_preserves_original_url(self, detector: UrlDetector) -> None:
        """Original URL is always preserved."""
        url = "https://www.instagram.com/p/CsEj0n9Kefd/"
        result = detector.detect(url)
        assert result.original_url == url
