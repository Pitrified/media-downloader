"""Post-processor protocol for the download pipeline."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol
from typing import runtime_checkable

if TYPE_CHECKING:
    from media_downloader.core.models import DownloadedMedia


@runtime_checkable
class PostProcessor(Protocol):
    """Protocol for post-processing hooks in the download pipeline.

    Post-processors enrich or transform a ``DownloadedMedia`` after
    download. They are applied sequentially by ``DownloadRouter``.
    """

    def process(self, media: DownloadedMedia) -> DownloadedMedia:
        """Process media synchronously.

        Args:
            media: Downloaded media to enrich.

        Returns:
            The same (or a new) ``DownloadedMedia`` instance.
        """
        ...

    async def aprocess(self, media: DownloadedMedia) -> DownloadedMedia:
        """Process media asynchronously.

        Args:
            media: Downloaded media to enrich.

        Returns:
            The same (or a new) ``DownloadedMedia`` instance.
        """
        ...
