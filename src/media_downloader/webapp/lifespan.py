"""FastAPI application lifespan manager.

Initializes the database, storage, transcriber, download router, and
background worker at startup. Cleans up on shutdown.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from contextlib import suppress
from typing import TYPE_CHECKING

from loguru import logger as lg

from media_downloader.db.service import DownloadDBService
from media_downloader.storage.media_storage import MediaStorage
from media_downloader.webapp.router_builder import build_download_router
from media_downloader.webapp.worker import run_worker

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastapi import FastAPI

    from media_downloader.config.downloader_config import DownloaderConfig


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan: setup and teardown of service resources.

    Initializes:
        - Database (SQLite with WAL mode)
        - Media storage directory
        - Transcriber (if configured)
        - Download router with providers and post-processors
        - Background worker task

    Args:
        app: The FastAPI application instance.

    Yields:
        Control back to the application.
    """
    config: DownloaderConfig = app.state.downloader_config

    # Database
    db = DownloadDBService(db_path=config.db_path)
    await db.init_db()
    app.state.db = db

    # Media storage
    storage = MediaStorage(base_dir=config.media_base_dir)
    app.state.storage = storage

    # Transcriber (may be None if transcription disabled)
    transcriber = None
    if config.providers.transcription is not None:
        transcriber = config.providers.transcription.create_transcriber()
        lg.info(f"Transcriber ready: {transcriber.provider_name}")
    app.state.transcriber = transcriber

    # Download router
    dl_router = build_download_router(config, storage, transcriber=transcriber)
    app.state.dl_router = dl_router

    # Background worker
    worker_task = asyncio.create_task(run_worker(db, dl_router))
    app.state.worker_task = worker_task

    yield

    # Shutdown
    worker_task.cancel()
    with suppress(asyncio.CancelledError):
        await worker_task

    await db.close()
    lg.info("Application shutdown complete")
