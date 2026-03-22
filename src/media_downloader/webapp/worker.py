"""Background worker for processing queued download jobs.

Polls the database for pending jobs and processes them sequentially
through the ``DownloadRouter`` pipeline.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from loguru import logger as lg

if TYPE_CHECKING:
    from media_downloader.core.router import DownloadRouter
    from media_downloader.db.service import DownloadDBService


async def run_worker(
    db: DownloadDBService,
    dl_router: DownloadRouter,
    poll_interval: float = 2.0,
) -> None:
    """Poll for pending jobs and process them.

    Runs indefinitely until cancelled. Processes one job at a time.

    Args:
        db: Database service for job state management.
        dl_router: Download router for executing downloads.
        poll_interval: Seconds between polls when idle.
    """
    lg.info("Background worker started")
    while True:
        try:
            jobs = await db.get_pending_jobs()
            if not jobs:
                await asyncio.sleep(poll_interval)
                continue

            for job in jobs:
                await _process_job(db, dl_router, job.id, job.url)

        except asyncio.CancelledError:
            lg.info("Background worker shutting down")
            raise
        except Exception:  # noqa: BLE001
            lg.exception("Worker error, retrying after delay")
            await asyncio.sleep(poll_interval)


async def _process_job(
    db: DownloadDBService,
    dl_router: DownloadRouter,
    job_id: str,
    url: str,
) -> None:
    """Process a single download job.

    Args:
        db: Database service.
        dl_router: Download router.
        job_id: The job identifier.
        url: The URL to download.
    """
    lg.info(f"Processing job {job_id}: {url}")
    await db.mark_running(job_id)

    try:
        media = await dl_router.adownload(url)
        await db.mark_completed(job_id, media)
    except Exception as exc:  # noqa: BLE001
        lg.exception(f"Job {job_id} failed")
        await db.mark_failed(job_id, str(exc))
