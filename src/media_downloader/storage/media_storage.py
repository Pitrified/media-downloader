"""Media file storage with structured folder hierarchy.

``MediaStorage`` manages the on-disk directory layout for downloaded media.
Each download gets a folder keyed by ``{source}/{source_id}/``, with files
distinguished by role (``video``, ``thumbnail``, ``audio``, etc.).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger as lg

if TYPE_CHECKING:
    from pathlib import Path

    from media_downloader.core.models import SourceType


class MediaStorage:
    """Manages media file paths and directory creation.

    Folder layout::

        {base_dir}/{source_value}/{source_id}/
            video.mp4
            thumbnail.jpg
            audio.wav

    Attributes:
        base_dir:
            Root directory for all media storage.
    """

    def __init__(self, base_dir: Path) -> None:
        """Initialize with the base media directory.

        Args:
            base_dir: Root directory for all media storage.
        """
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def source_dir(self, source: SourceType, source_id: str) -> Path:
        """Return the directory for a specific download.

        Args:
            source: The content source type.
            source_id: Platform-specific content identifier.

        Returns:
            Path to the download's directory (created if needed).
        """
        d = self.base_dir / source.value / source_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def media_path(
        self,
        source: SourceType,
        source_id: str,
        *,
        role: str = "video",
        ext: str = "mp4",
    ) -> Path:
        """Build a file path for a media role within a download's directory.

        Args:
            source: The content source type.
            source_id: Platform-specific content identifier.
            role: File role name (e.g. ``"video"``, ``"thumbnail"``, ``"audio"``).
            ext: File extension without the leading dot.

        Returns:
            Full path to the media file. Parent directory is created.
        """
        d = self.source_dir(source, source_id)
        return d / f"{role}.{ext}"

    def list_files(self, source: SourceType, source_id: str) -> list[Path]:
        """List all files for a given download.

        Args:
            source: The content source type.
            source_id: Platform-specific content identifier.

        Returns:
            Sorted list of file paths in the download directory.
            Empty list if the directory does not exist.
        """
        d = self.base_dir / source.value / source_id
        if not d.exists():
            return []
        return sorted(d.iterdir())

    def cleanup(self, source: SourceType, source_id: str) -> None:
        """Remove all files for a download (but keep the directory structure).

        Args:
            source: The content source type.
            source_id: Platform-specific content identifier.
        """
        d = self.base_dir / source.value / source_id
        if not d.exists():
            return
        for f in d.iterdir():
            if f.is_file():
                lg.debug(f"Removing {f}")
                f.unlink()
