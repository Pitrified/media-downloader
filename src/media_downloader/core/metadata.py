"""Source-specific metadata models.

Each download provider can attach a typed metadata object to
``DownloadedMedia.metadata``. The ``SourceMetadata`` union enables
type-safe dispatching in downstream consumers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass
class InstagramMetadata:
    """Metadata specific to Instagram posts.

    Attributes:
        shortcode:
            The post's shortcode (URL slug).
        owner_username:
            Username of the post owner.
        timestamp:
            When the post was published.
        like_count:
            Number of likes at download time.
        is_video:
            Whether the post is a video (vs. image/carousel).
    """

    shortcode: str
    owner_username: str = ""
    timestamp: datetime | None = None
    like_count: int = 0
    is_video: bool = False


@dataclass
class YtDlpMetadata:
    """Metadata specific to yt-dlp downloads (YouTube, TikTok, etc.).

    Attributes:
        extractor:
            The yt-dlp extractor name (e.g. ``"youtube"``, ``"TikTok"``).
        title:
            Video title.
        uploader:
            Channel or uploader name.
        duration:
            Video duration in seconds.
        upload_date:
            Upload date as reported by yt-dlp (``YYYYMMDD`` string).
        view_count:
            View count at download time.
    """

    extractor: str
    title: str = ""
    uploader: str = ""
    duration: float = 0.0
    upload_date: str = ""
    view_count: int = 0


@dataclass
class WebRecipeMetadata:
    """Metadata specific to web recipe downloads.

    Attributes:
        recipe_title:
            Name of the recipe.
        host:
            Website hostname the recipe was scraped from.
        total_time:
            Total cooking time as reported by the scraper.
        yields:
            Serving size / yield string.
        ingredients:
            List of ingredient strings.
        instructions:
            Cooking instructions as a single text block.
    """

    recipe_title: str = ""
    host: str = ""
    total_time: str = ""
    yields: str = ""
    ingredients: list[str] | None = None
    instructions: str = ""


SourceMetadata = InstagramMetadata | YtDlpMetadata | WebRecipeMetadata
"""Union of all provider-specific metadata types."""
