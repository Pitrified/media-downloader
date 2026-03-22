"""Synchronous download endpoint.

Provides ``POST /download`` for immediate, blocking downloads. The
response includes the download result without going through the
background job queue.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from media_downloader.core.router import NoDownloaderForSourceError
from media_downloader.webapp.schemas import DownloadRequest
from media_downloader.webapp.schemas import DownloadResponse

router = APIRouter(tags=["download"])


@router.post("/download", response_model=DownloadResponse)
async def download_sync(request: Request, body: DownloadRequest) -> DownloadResponse:
    """Download media immediately (blocking).

    Args:
        request: FastAPI request (provides access to app state).
        body: Download request with URL.

    Returns:
        Download result with source info, files, and optional transcription.
    """
    dl_router = request.app.state.dl_router

    try:
        media = await dl_router.adownload(body.url)
    except NoDownloaderForSourceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return DownloadResponse(
        source=media.source.value,
        source_id=media.source_id,
        files=[str(f) for f in media.all_files],
        caption=media.caption,
        transcript=media.transcript,
        language=media.language,
    )
