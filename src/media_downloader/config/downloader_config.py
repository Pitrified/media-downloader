"""Downloader configuration models.

Shape-only definitions for the download service settings. These config
models define typed fields and defaults but never read environment
variables or runtime state. Actual values are loaded by the paired
Params classes.
"""

from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import Any

from pydantic import ConfigDict

from media_downloader.data_models.basemodel_kwargs import BaseModelKwargs


class ProvidersConfig(BaseModelKwargs):
    """Configuration for which download/post-processing providers are enabled.

    Attributes:
        instagram_enabled:
            Enable Instagram downloading.
        video_enabled:
            Enable yt-dlp (YouTube, TikTok) downloading.
        web_recipe_enabled:
            Enable web recipe scraping.
        transcription:
            Transcription provider config. None means transcription
            is disabled. Typed as ``Any`` to avoid a hard dependency
            on ``llm-core`` at import time; at runtime it is either
            ``None`` or a ``TranscriptionConfig`` subclass.
    """

    instagram_enabled: bool = True
    video_enabled: bool = True
    web_recipe_enabled: bool = True
    transcription: Any = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class DownloaderConfig(BaseModelKwargs):
    """Top-level configuration for the download service.

    Attributes:
        db_path:
            Path to the SQLite database file.
        media_base_dir:
            Root directory for downloaded media files.
        providers:
            Provider enable/disable flags and transcription config.
        yt_dlp_format:
            yt-dlp format selection string.
        log_level:
            Logging level.
    """

    db_path: Path
    media_base_dir: Path
    providers: ProvidersConfig = ProvidersConfig()
    yt_dlp_format: str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    log_level: str = "INFO"

    model_config = ConfigDict(arbitrary_types_allowed=True)
