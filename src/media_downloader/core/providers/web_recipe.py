"""Web recipe download provider.

Downloads and parses structured recipe data from cooking websites.
Uses ``recipe-scrapers`` as the primary parser with ``trafilatura``
as a fallback for unstructured pages. Requires the ``recipe`` optional
dependency group.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from loguru import logger as lg

from media_downloader.core.metadata import WebRecipeMetadata
from media_downloader.core.models import DownloadedMedia
from media_downloader.core.models import SourceType

if TYPE_CHECKING:
    from pathlib import Path

    from media_downloader.storage.media_storage import MediaStorage


class WebRecipeDownloader:
    """Download and parse recipes from cooking websites.

    Attributes:
        storage:
            Media storage instance for file persistence.
        supported_sources:
            Source types handled by this provider.
    """

    supported_sources: frozenset[SourceType] = frozenset({SourceType.WEB_RECIPE})

    def __init__(self, storage: MediaStorage) -> None:
        """Initialize with media storage.

        Args:
            storage: Media storage instance for file persistence.
        """
        self.storage = storage

    def download(self, url: str, source_id: str) -> DownloadedMedia:  # noqa: ARG002
        """Download and parse a recipe from a URL.

        Args:
            url: Recipe page URL.
            source_id: URL used as identifier for recipes.

        Returns:
            Populated ``DownloadedMedia`` with recipe text as caption.
        """
        import hashlib  # noqa: PLC0415

        lg.info(f"Downloading recipe: {url}")

        # Use a hash of the URL as the folder name for recipes
        folder_id = hashlib.sha256(url.encode()).hexdigest()[:16]
        target_dir = self.storage.source_dir(SourceType.WEB_RECIPE, folder_id)

        recipe_text, metadata = self._scrape_recipe(url)

        # Save recipe text to file
        recipe_fp = target_dir / "recipe.txt"
        recipe_fp.write_text(recipe_text, encoding="utf-8")
        all_files: list[Path] = [recipe_fp]

        return DownloadedMedia(
            source=SourceType.WEB_RECIPE,
            source_id=folder_id,
            original_url=url,
            all_files=all_files,
            caption=recipe_text,
            metadata=metadata,
        )

    async def adownload(self, url: str, source_id: str) -> DownloadedMedia:
        """Async wrapper - runs download in a thread pool.

        Args:
            url: Recipe page URL.
            source_id: URL used as identifier.

        Returns:
            Populated ``DownloadedMedia``.
        """
        return await asyncio.to_thread(self.download, url, source_id)

    def _scrape_recipe(self, url: str) -> tuple[str, WebRecipeMetadata]:
        """Try recipe-scrapers first, fall back to trafilatura.

        Args:
            url: Recipe page URL.

        Returns:
            Tuple of (recipe_text, metadata).
        """
        try:
            return self._scrape_with_recipe_scrapers(url)
        except Exception:  # noqa: BLE001
            lg.warning(f"recipe-scrapers failed for {url}, trying trafilatura")
            return self._scrape_with_trafilatura(url)

    def _scrape_with_recipe_scrapers(
        self,
        url: str,
    ) -> tuple[str, WebRecipeMetadata]:
        """Extract structured recipe data using recipe-scrapers.

        Args:
            url: Recipe page URL.

        Returns:
            Tuple of (formatted recipe text, metadata).
        """
        from urllib.request import urlopen  # noqa: PLC0415

        from recipe_scrapers import scrape_html  # noqa: PLC0415

        html = urlopen(url).read().decode("utf-8")  # noqa: S310
        scraper = scrape_html(html=html, org_url=url)

        title = scraper.title()
        ingredients = scraper.ingredients()
        instructions = scraper.instructions()
        total_time = str(scraper.total_time()) if scraper.total_time() else ""
        yields = scraper.yields()
        host = scraper.host()

        # Build readable text
        parts = [f"# {title}", ""]
        if ingredients:
            parts.append("## Ingredients")
            parts.extend(f"- {ing}" for ing in ingredients)
            parts.append("")
        if instructions:
            parts.append("## Instructions")
            parts.append(instructions)

        recipe_text = "\n".join(parts)

        metadata = WebRecipeMetadata(
            recipe_title=title,
            host=host,
            total_time=total_time,
            yields=yields,
            ingredients=ingredients,
            instructions=instructions,
        )

        return recipe_text, metadata

    def _scrape_with_trafilatura(self, url: str) -> tuple[str, WebRecipeMetadata]:
        """Extract page content using trafilatura as a fallback.

        Args:
            url: Web page URL.

        Returns:
            Tuple of (extracted text, minimal metadata).
        """
        import trafilatura  # noqa: PLC0415

        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            msg = f"Failed to fetch URL: {url}"
            raise RuntimeError(msg)

        text = trafilatura.extract(downloaded) or ""

        from urllib.parse import urlparse  # noqa: PLC0415

        host = urlparse(url).netloc

        metadata = WebRecipeMetadata(
            host=host,
            instructions=text,
        )

        return text, metadata
