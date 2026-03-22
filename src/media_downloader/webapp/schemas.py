"""Request and response schemas for the download API."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003

from pydantic import BaseModel


class DownloadRequest(BaseModel):
    """Request to download media from a URL.

    Attributes:
        url:
            The URL to download media from.
        download_video:
            Whether to download video content. Respected by yt-dlp
            and instaloader providers.
    """

    url: str
    download_video: bool = True


class MediaFileRead(BaseModel):
    """Read-only representation of a media file.

    Attributes:
        file_path:
            Relative path from media base directory.
        role:
            File role (video, thumbnail, audio, recipe, etc.).
        media_on_disk:
            Whether the file currently exists on disk.
    """

    file_path: str
    role: str
    media_on_disk: bool


class DownloadJobRead(BaseModel):
    """Read-only representation of a download job.

    Attributes:
        id:
            Job identifier.
        url:
            Original URL submitted.
        source:
            Detected source type.
        source_id:
            Platform-specific content identifier.
        status:
            Job lifecycle state.
        error:
            Error message if failed.
        created_at:
            Job creation timestamp.
        updated_at:
            Last update timestamp.
        transcript:
            Transcription text if available.
        language:
            Detected language from transcription.
        media_files:
            Associated media files.
    """

    id: str
    url: str
    source: str
    source_id: str
    status: str
    error: str | None = None
    created_at: datetime
    updated_at: datetime
    transcript: str | None = None
    language: str | None = None
    media_files: list[MediaFileRead] = []


class DownloadResponse(BaseModel):
    """Response for a synchronous download request.

    Attributes:
        source:
            Detected source type.
        source_id:
            Platform-specific content identifier.
        files:
            List of downloaded file paths.
        caption:
            Content caption or description.
        transcript:
            Transcription text if available.
        language:
            Detected language from transcription.
    """

    source: str
    source_id: str
    files: list[str]
    caption: str = ""
    transcript: str | None = None
    language: str | None = None
