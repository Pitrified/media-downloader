"""yt-dlp download provider for YouTube, TikTok, and other video platforms.

Uses yt-dlp to download video content. Supports any site that yt-dlp handles.
Requires the ``yt-dlp`` optional dependency.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from loguru import logger as lg

from media_downloader.core.metadata import YtDlpMetadata
from media_downloader.core.models import DownloadedMedia
from media_downloader.core.models import SourceType

if TYPE_CHECKING:
    from pathlib import Path

    from media_downloader.storage.media_storage import MediaStorage

_DEFAULT_FORMAT = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"


class YtDlpDownloader:
    """Download video content via yt-dlp.

    Handles YouTube, TikTok, and any other platform supported by yt-dlp.

    Attributes:
        storage:
            Media storage instance for file persistence.
        format_str:
            yt-dlp format selection string.
        supported_sources:
            Source types handled by this provider.
    """

    supported_sources: frozenset[SourceType] = frozenset(
        {
            SourceType.YOUTUBE,
            SourceType.TIKTOK,
        }
    )

    def __init__(
        self,
        storage: MediaStorage,
        format_str: str = _DEFAULT_FORMAT,
    ) -> None:
        """Initialize with media storage and format selection.

        Args:
            storage: Media storage instance for file persistence.
            format_str: yt-dlp format selection string.
        """
        self.storage = storage
        self.format_str = format_str

    def download(self, url: str, source_id: str) -> DownloadedMedia:
        """Download a video via yt-dlp.

        Args:
            url: Original video URL.
            source_id: Platform-specific video identifier.

        Returns:
            Populated ``DownloadedMedia``.
        """
        import yt_dlp  # noqa: PLC0415

        lg.info(f"Downloading via yt-dlp: {source_id} ({url})")

        # Determine source type for storage path
        is_youtube = "youtube" in url or "youtu.be" in url
        source = SourceType.YOUTUBE if is_youtube else SourceType.TIKTOK
        target_dir = self.storage.source_dir(source, source_id)
        output_template = str(target_dir / "video.%(ext)s")

        ydl_opts = {
            "format": self.format_str,
            "outtmpl": output_template,
            "writeinfojson": False,
            "writethumbnail": True,
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
            info = ydl.extract_info(url, download=True)

        if info is None:
            msg = f"yt-dlp returned no info for URL: {url}"
            raise RuntimeError(msg)

        # Collect files
        video_file = None
        thumbnail_file = None
        all_files: list[Path] = []

        for fp in sorted(target_dir.iterdir()):
            if not fp.is_file():
                continue
            all_files.append(fp)
            suffix = fp.suffix.lower()
            if suffix in {".mp4", ".webm", ".mkv"} and video_file is None:
                video_file = fp
            elif (
                suffix in {".jpg", ".jpeg", ".png", ".webp"} and thumbnail_file is None
            ):
                thumbnail_file = fp

        metadata = YtDlpMetadata(
            extractor=str(info.get("extractor", "")),
            title=str(info.get("title", "")),
            uploader=str(info.get("uploader", "")),
            duration=float(info.get("duration", 0) or 0),
            upload_date=str(info.get("upload_date", "")),
            view_count=int(info.get("view_count", 0) or 0),
        )

        return DownloadedMedia(
            source=source,
            source_id=source_id,
            original_url=url,
            video_file=video_file,
            thumbnail_file=thumbnail_file,
            all_files=all_files,
            caption=info.get("description", "") or "",
            metadata=metadata,
        )

    async def adownload(self, url: str, source_id: str) -> DownloadedMedia:
        """Async wrapper - runs download in a thread pool.

        Args:
            url: Original video URL.
            source_id: Platform-specific video identifier.

        Returns:
            Populated ``DownloadedMedia``.
        """
        return await asyncio.to_thread(self.download, url, source_id)
