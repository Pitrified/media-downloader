"""Job queue endpoints.

Provides endpoints for submitting download jobs to the background queue
and checking their status. Jobs are processed by the background worker.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

from media_downloader.webapp.schemas import DownloadJobRead
from media_downloader.webapp.schemas import DownloadRequest
from media_downloader.webapp.schemas import MediaFileRead

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=DownloadJobRead, status_code=201)
async def create_job(request: Request, body: DownloadRequest) -> DownloadJobRead:
    """Submit a download job to the background queue.

    Args:
        request: FastAPI request.
        body: Download request with URL.

    Returns:
        The created job in pending state.
    """
    db = request.app.state.db
    job = await db.create_job(body.url)

    return DownloadJobRead(
        id=job.id,
        url=job.url,
        source=job.source,
        source_id=job.source_id,
        status=job.status,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
        transcript=job.transcript,
        language=job.language,
    )


@router.get("/{job_id}", response_model=DownloadJobRead)
async def get_job(request: Request, job_id: str) -> DownloadJobRead:
    """Get the status and result of a download job.

    Args:
        request: FastAPI request.
        job_id: The job identifier.

    Returns:
        Job details including status, files, and optional transcription.
    """
    db = request.app.state.db
    job = await db.get_job(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    media_files = [
        MediaFileRead(
            file_path=mf.file_path,
            role=mf.role,
            media_on_disk=mf.media_on_disk,
        )
        for mf in (job.media_files or [])
    ]

    return DownloadJobRead(
        id=job.id,
        url=job.url,
        source=job.source,
        source_id=job.source_id,
        status=job.status,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
        transcript=job.transcript,
        language=job.language,
        media_files=media_files,
    )
