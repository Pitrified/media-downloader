"""Tests for DownloadRouter."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING

import pytest

from media_downloader.core.models import DownloadedMedia
from media_downloader.core.models import SourceType
from media_downloader.core.router import DownloadRouter
from media_downloader.core.router import NoDownloaderForSourceError
from media_downloader.storage.media_storage import MediaStorage

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class FakeDownloader:
    """Fake downloader for testing."""

    storage: MediaStorage
    _supported: frozenset[SourceType] = field(default_factory=frozenset)
    download_count: int = 0

    @property
    def supported_sources(self) -> frozenset[SourceType]:
        """Return supported source types."""
        return self._supported

    def download(self, url: str, source_id: str) -> DownloadedMedia:
        """Perform a fake download."""
        self.download_count += 1
        return DownloadedMedia(
            source=SourceType.YOUTUBE,
            source_id=source_id,
            original_url=url,
        )

    async def adownload(self, url: str, source_id: str) -> DownloadedMedia:
        """Perform a fake async download."""
        return self.download(url, source_id)


@dataclass
class FakePostProcessor:
    """Fake post-processor for testing."""

    process_count: int = 0

    def process(self, media: DownloadedMedia) -> DownloadedMedia:
        """Apply fake processing."""
        self.process_count += 1
        media.caption = "processed"
        return media

    async def aprocess(self, media: DownloadedMedia) -> DownloadedMedia:
        """Apply fake processing asynchronously."""
        return self.process(media)


def test_router_dispatches_to_correct_downloader(tmp_path: Path) -> None:
    """Router dispatches to the downloader matching detected source."""
    storage = MediaStorage(base_dir=tmp_path)
    dl = FakeDownloader(
        storage=storage,
        _supported=frozenset({SourceType.YOUTUBE}),
    )
    router = DownloadRouter(downloaders=[dl])
    media = router.download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert media.source_id == "dQw4w9WgXcQ"
    assert dl.download_count == 1


def test_router_raises_for_unknown_source(tmp_path: Path) -> None:
    """Router raises when no downloader handles the source."""
    storage = MediaStorage(base_dir=tmp_path)
    dl = FakeDownloader(
        storage=storage,
        _supported=frozenset({SourceType.YOUTUBE}),
    )
    router = DownloadRouter(downloaders=[dl])
    with pytest.raises(NoDownloaderForSourceError):
        router.download("https://example.com/unknown")


def test_router_applies_post_processors(tmp_path: Path) -> None:
    """Router applies post-processors after download."""
    storage = MediaStorage(base_dir=tmp_path)
    dl = FakeDownloader(
        storage=storage,
        _supported=frozenset({SourceType.YOUTUBE}),
    )
    pp = FakePostProcessor()
    router = DownloadRouter(downloaders=[dl], post_processors=[pp])
    media = router.download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert media.caption == "processed"
    assert pp.process_count == 1


def test_router_async_download(tmp_path: Path) -> None:
    """Router async download works correctly."""
    storage = MediaStorage(base_dir=tmp_path)
    dl = FakeDownloader(
        storage=storage,
        _supported=frozenset({SourceType.YOUTUBE}),
    )
    router = DownloadRouter(downloaders=[dl])
    media = asyncio.run(
        router.adownload("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
    )
    assert media.source_id == "dQw4w9WgXcQ"
