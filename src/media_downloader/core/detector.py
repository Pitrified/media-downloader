"""URL detection and source classification.

``UrlDetector`` examines a URL and determines which ``SourceType`` it
belongs to, along with extracting a platform-specific content identifier
when possible.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from media_downloader.core.models import SourceType


@dataclass
class DetectionResult:
    """Result of URL detection.

    Attributes:
        source:
            Detected content source.
        source_id:
            Platform-specific content identifier extracted from the URL.
            Falls back to the full URL when no ID can be parsed.
        original_url:
            The input URL, preserved for downstream use.
    """

    source: SourceType
    source_id: str
    original_url: str


# Instagram shortcode pattern: /p/SHORTCODE/ or /reel/SHORTCODE/
_INSTAGRAM_PATTERN = re.compile(
    r"instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)",
)

# YouTube video ID patterns
_YOUTUBE_PATTERNS = [
    re.compile(r"(?:youtube\.com/watch\?.*v=|youtu\.be/)([A-Za-z0-9_-]{11})"),
    re.compile(r"youtube\.com/shorts/([A-Za-z0-9_-]{11})"),
]

# TikTok video ID pattern
_TIKTOK_PATTERN = re.compile(
    r"tiktok\.com/.*?/video/(\d+)",
)

# Recipe sites - a non-exhaustive list of popular recipe hosts
_RECIPE_HOSTS = frozenset(
    {
        "allrecipes.com",
        "bbcgoodfood.com",
        "bonappetit.com",
        "budgetbytes.com",
        "cookieandkate.com",
        "delish.com",
        "epicurious.com",
        "food52.com",
        "foodnetwork.com",
        "minimalistbaker.com",
        "seriouseats.com",
        "simplyrecipes.com",
        "smittenkitchen.com",
        "tastykitchen.com",
        "thekitchn.com",
    }
)


class UrlDetector:
    """Classify URLs into source types and extract content identifiers."""

    def detect(self, url: str) -> DetectionResult:
        """Analyse a URL and return source type + content identifier.

        Args:
            url: The URL to classify.

        Returns:
            DetectionResult with source, source_id, and original_url.
        """
        # Instagram
        match = _INSTAGRAM_PATTERN.search(url)
        if match:
            return DetectionResult(
                source=SourceType.INSTAGRAM,
                source_id=match.group(1),
                original_url=url,
            )

        # YouTube
        for pattern in _YOUTUBE_PATTERNS:
            match = pattern.search(url)
            if match:
                return DetectionResult(
                    source=SourceType.YOUTUBE,
                    source_id=match.group(1),
                    original_url=url,
                )

        # TikTok
        match = _TIKTOK_PATTERN.search(url)
        if match:
            return DetectionResult(
                source=SourceType.TIKTOK,
                source_id=match.group(1),
                original_url=url,
            )

        # Recipe sites
        url_lower = url.lower()
        for host in _RECIPE_HOSTS:
            if host in url_lower:
                return DetectionResult(
                    source=SourceType.WEB_RECIPE,
                    source_id=url,
                    original_url=url,
                )

        return DetectionResult(
            source=SourceType.UNKNOWN,
            source_id=url,
            original_url=url,
        )
