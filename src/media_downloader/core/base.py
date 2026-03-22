"""Base downloader protocol.

All download providers implement this protocol so that ``DownloadRouter``
can dispatch to them polymorphically.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol
from typing import runtime_checkable

if TYPE_CHECKING:
    from media_downloader.core.models import DownloadedMedia
    from media_downloader.core.models import SourceType
    from media_downloader.storage.media_storage import MediaStorage


@runtime_checkable
class BaseDownloader(Protocol):
    """Protocol for media download providers.

    Each implementation handles one or more ``SourceType`` values and
    knows how to fetch content from the corresponding platform.
    """

    @property
    def supported_sources(self) -> frozenset[SourceType]:
        """Source types this downloader can handle."""
        ...

    @property
    def storage(self) -> MediaStorage:
        """Media storage instance used for persisting files."""
        ...

    def download(self, url: str, source_id: str) -> DownloadedMedia:
        """Download media synchronously.

        Args:
            url: The original URL to download.
            source_id: Platform-specific content identifier.

        Returns:
            Populated ``DownloadedMedia`` with files written to storage.
        """
        ...

    async def adownload(self, url: str, source_id: str) -> DownloadedMedia:
        """Download media asynchronously.

        Args:
            url: The original URL to download.
            source_id: Platform-specific content identifier.

        Returns:
            Populated ``DownloadedMedia`` with files written to storage.
        """
        ...
