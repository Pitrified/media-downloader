"""Core data models for downloaded media.

Defines the primary data structures used throughout the download pipeline:
``SourceType`` for identifying content origins, ``DownloadedMedia`` for
representing a completed download with optional transcription, and
``JobStatus`` for tracking asynchronous download job state.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from llm_core.transcription.base import TranscriptionResult

    from media_downloader.core.metadata import SourceMetadata


class SourceType(Enum):
    """Content source identifier."""

    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    WEB_RECIPE = "web_recipe"
    UNKNOWN = "unknown"


class JobStatus(Enum):
    """Asynchronous download job lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DownloadedMedia:
    """Result of a successful media download.

    Populated by a ``BaseDownloader`` implementation and enriched by
    post-processing hooks (e.g. ``TranscriptionHook``).

    Attributes:
        source:
            Content origin (Instagram, YouTube, etc.).
        source_id:
            Platform-specific unique identifier for the content.
        original_url:
            The URL that was submitted for download.
        video_file:
            Path to the downloaded video file, if any.
        thumbnail_file:
            Path to a thumbnail image, if any.
        audio_file:
            Path to the audio file (either downloaded directly or
            extracted from video by a post-processor).
        all_files:
            Every file persisted to disk for this download.
        caption:
            Text caption or description from the source platform.
        transcription:
            Result from the transcription post-processor. ``None``
            when transcription is disabled or no audio was available.
        metadata:
            Provider-specific metadata (Instagram, yt-dlp, recipe, etc.).
    """

    source: SourceType
    source_id: str
    original_url: str
    video_file: Path | None = None
    thumbnail_file: Path | None = None
    audio_file: Path | None = None
    all_files: list[Path] = field(default_factory=list)
    caption: str = ""
    transcription: TranscriptionResult | None = None
    metadata: SourceMetadata | None = None

    @property
    def language(self) -> str | None:
        """Language from transcription if available, else None."""
        return self.transcription.language if self.transcription else None

    @property
    def transcript(self) -> str | None:
        """Transcript text if available, else None."""
        return self.transcription.text if self.transcription else None
