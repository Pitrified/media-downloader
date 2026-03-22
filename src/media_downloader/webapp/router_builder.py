"""Download router builder.

Assembles a ``DownloadRouter`` from the service configuration,
wiring up enabled providers and post-processing hooks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from media_downloader.core.detector import UrlDetector
from media_downloader.core.router import DownloadRouter

if TYPE_CHECKING:
    from llm_core.transcription.base import BaseTranscriber

    from media_downloader.config.downloader_config import DownloaderConfig
    from media_downloader.core.base import BaseDownloader
    from media_downloader.post_processing.base import PostProcessor
    from media_downloader.storage.media_storage import MediaStorage


def build_download_router(
    config: DownloaderConfig,
    storage: MediaStorage,
    transcriber: BaseTranscriber | None = None,
) -> DownloadRouter:
    """Assemble a DownloadRouter from config and runtime dependencies.

    Args:
        config: The download service configuration.
        storage: Media storage instance.
        transcriber: Optional transcriber for audio post-processing.

    Returns:
        Configured ``DownloadRouter``.
    """
    providers: list[BaseDownloader] = []

    if config.providers.instagram_enabled:
        from media_downloader.core.providers.instagram import (  # noqa: PLC0415
            InstaDownloader,
        )

        providers.append(InstaDownloader(storage=storage))

    if config.providers.video_enabled:
        from media_downloader.core.providers.yt_dlp import (  # noqa: PLC0415
            YtDlpDownloader,
        )

        providers.append(
            YtDlpDownloader(storage=storage, format_str=config.yt_dlp_format),
        )

    if config.providers.web_recipe_enabled:
        from media_downloader.core.providers.web_recipe import (  # noqa: PLC0415
            WebRecipeDownloader,
        )

        providers.append(WebRecipeDownloader(storage=storage))

    post_processors: list[PostProcessor] = []
    if transcriber is not None:
        from media_downloader.post_processing.transcription import (  # noqa: PLC0415
            TranscriptionHook,
        )

        audio_format = _audio_format_for(transcriber)
        post_processors.append(
            TranscriptionHook(
                transcriber=transcriber,
                storage=storage,
                audio_format=audio_format,
            ),
        )

    return DownloadRouter(
        downloaders=providers,
        detector=UrlDetector(),
        post_processors=post_processors,
    )


def _audio_format_for(transcriber: BaseTranscriber) -> str:
    """Pick the best audio extraction format for the given provider.

    Args:
        transcriber: The transcription provider.

    Returns:
        ``"mp3"`` for OpenAI API, ``"wav"`` for local providers.
    """
    if transcriber.provider_name == "openai_api":
        return "mp3"
    return "wav"
