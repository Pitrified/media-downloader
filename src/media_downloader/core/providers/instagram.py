"""Instagram download provider using instaloader.

Downloads public Instagram posts (images, videos, reels) without login.
Requires the ``instaloader`` optional dependency.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from loguru import logger as lg

from media_downloader.core.metadata import InstagramMetadata
from media_downloader.core.models import DownloadedMedia
from media_downloader.core.models import SourceType

if TYPE_CHECKING:
    from pathlib import Path

    from media_downloader.storage.media_storage import MediaStorage


class InstaDownloader:
    """Download public Instagram posts via instaloader.

    Attributes:
        storage:
            Media storage instance for file persistence.
        supported_sources:
            Source types handled by this provider.
    """

    supported_sources: frozenset[SourceType] = frozenset({SourceType.INSTAGRAM})

    def __init__(self, storage: MediaStorage) -> None:
        """Initialize with media storage.

        Args:
            storage: Media storage instance for file persistence.
        """
        self.storage = storage

    def download(self, url: str, source_id: str) -> DownloadedMedia:
        """Download an Instagram post by shortcode.

        Args:
            url: Original Instagram URL.
            source_id: Post shortcode.

        Returns:
            Populated ``DownloadedMedia``.
        """
        import instaloader  # noqa: PLC0415

        lg.info(f"Downloading Instagram post: {source_id}")
        loader = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=True,
            save_metadata=False,
            post_metadata_txt_pattern="",
        )

        post = instaloader.Post.from_shortcode(loader.context, source_id)
        target_dir = self.storage.source_dir(SourceType.INSTAGRAM, source_id)

        # Download into the target directory
        loader.download_post(post, target=str(target_dir))

        # Collect downloaded files
        video_file = None
        thumbnail_file = None
        all_files: list[Path] = []

        for fp in sorted(target_dir.iterdir()):
            if not fp.is_file():
                continue
            all_files.append(fp)
            suffix = fp.suffix.lower()
            if suffix in {".mp4", ".webm"} and video_file is None:
                video_file = fp
            elif suffix in {".jpg", ".jpeg", ".png"} and thumbnail_file is None:
                thumbnail_file = fp

        metadata = InstagramMetadata(
            shortcode=source_id,
            owner_username=post.owner_username,
            timestamp=post.date_utc,
            like_count=post.likes,
            is_video=post.is_video,
        )

        return DownloadedMedia(
            source=SourceType.INSTAGRAM,
            source_id=source_id,
            original_url=url,
            video_file=video_file,
            thumbnail_file=thumbnail_file,
            all_files=all_files,
            caption=post.caption or "",
            metadata=metadata,
        )

    async def adownload(self, url: str, source_id: str) -> DownloadedMedia:
        """Async wrapper - runs download in a thread pool.

        Args:
            url: Original Instagram URL.
            source_id: Post shortcode.

        Returns:
            Populated ``DownloadedMedia``.
        """
        return await asyncio.to_thread(self.download, url, source_id)
