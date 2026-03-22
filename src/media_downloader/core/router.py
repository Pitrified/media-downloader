"""Download router: detect source, dispatch to provider, apply post-processors.

The ``DownloadRouter`` is the main entry point for the download pipeline.
It uses ``UrlDetector`` to classify a URL, finds the appropriate
``BaseDownloader``, executes the download, and then applies
post-processing hooks sequentially.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger as lg

from media_downloader.core.detector import UrlDetector

if TYPE_CHECKING:
    from media_downloader.core.base import BaseDownloader
    from media_downloader.core.models import DownloadedMedia
    from media_downloader.core.models import SourceType
    from media_downloader.post_processing.base import PostProcessor


class NoDownloaderForSourceError(Exception):
    """Raised when no downloader is registered for a detected source type."""

    def __init__(self, source: SourceType) -> None:
        """Initialize with the unhandled source type.

        Args:
            source: The source type with no registered downloader.
        """
        self.source = source
        super().__init__(f"No downloader registered for source: {source.value}")


class DownloadRouter:
    """Detect URL source, dispatch download, and apply post-processors.

    Attributes:
        detector:
            URL classifier.
        downloaders:
            Registered download providers.
        post_processors:
            Hooks applied after download (e.g. transcription).
    """

    def __init__(
        self,
        downloaders: list[BaseDownloader],
        detector: UrlDetector | None = None,
        post_processors: list[PostProcessor] | None = None,
    ) -> None:
        """Initialize with downloaders, detector, and optional post-processors.

        Args:
            downloaders: Available download providers.
            detector: URL classifier. Defaults to a new ``UrlDetector``.
            post_processors: Hooks applied after each download.
        """
        self.detector = detector or UrlDetector()
        self.post_processors: list[PostProcessor] = post_processors or []

        # Build a lookup mapping source types to downloaders
        self._source_map: dict[SourceType, BaseDownloader] = {}
        for dl in downloaders:
            for src in dl.supported_sources:
                self._source_map[src] = dl

    def download(self, url: str) -> DownloadedMedia:
        """Run the full download pipeline synchronously.

        Args:
            url: The URL to download.

        Returns:
            Enriched ``DownloadedMedia`` after all post-processors.

        Raises:
            NoDownloaderForSourceError: If no provider handles the detected source.
        """
        detection = self.detector.detect(url)
        lg.info(f"Detected {detection.source.value} for URL: {url}")

        downloader = self._source_map.get(detection.source)
        if downloader is None:
            raise NoDownloaderForSourceError(detection.source)

        media = downloader.download(url, detection.source_id)

        for pp in self.post_processors:
            media = pp.process(media)

        return media

    async def adownload(self, url: str) -> DownloadedMedia:
        """Run the full download pipeline asynchronously.

        Args:
            url: The URL to download.

        Returns:
            Enriched ``DownloadedMedia`` after all post-processors.

        Raises:
            NoDownloaderForSourceError: If no provider handles the detected source.
        """
        detection = self.detector.detect(url)
        lg.info(f"Detected {detection.source.value} for URL: {url}")

        downloader = self._source_map.get(detection.source)
        if downloader is None:
            raise NoDownloaderForSourceError(detection.source)

        media = await downloader.adownload(url, detection.source_id)

        for pp in self.post_processors:
            media = await pp.aprocess(media)

        return media
