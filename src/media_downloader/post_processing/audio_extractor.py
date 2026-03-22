"""Audio extraction from video files using pydub.

Provides ``extract_audio`` for synchronous extraction and
``extract_audio_async`` for use in async contexts. The extraction
normalises audio to mono 16 kHz 16-bit PCM - the format expected by
Whisper and faster-whisper internals.

Requires ``pydub`` (optional dependency) and ``ffmpeg`` on the system PATH.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from loguru import logger as lg

if TYPE_CHECKING:
    from pathlib import Path

# File extensions that can go directly to a transcriber without extraction.
_AUDIO_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".aac",
        ".flac",
        ".m4a",
        ".mp3",
        ".mpeg",
        ".mpga",
        ".ogg",
        ".wav",
    }
)

# Video extensions that require audio extraction before transcription.
_VIDEO_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".avi",
        ".mkv",
        ".mov",
        ".mp4",
        ".ts",
        ".webm",
    }
)


def needs_extraction(fp: Path) -> bool:
    """Return True if the file is a video that requires audio extraction.

    Args:
        fp: Path to check.

    Returns:
        True if the file extension is a known video format.
    """
    return fp.suffix.lower() in _VIDEO_EXTENSIONS


def is_audio_file(fp: Path) -> bool:
    """Return True if the file is a known audio format.

    Args:
        fp: Path to check.

    Returns:
        True if the file extension is a known audio format.
    """
    return fp.suffix.lower() in _AUDIO_EXTENSIONS


def extract_audio(
    video_fp: Path,
    audio_fp: Path,
    *,
    channels: int = 1,
    frame_rate: int = 16_000,
    sample_width: int = 2,
    audio_format: str = "wav",
) -> Path:
    """Extract and normalise audio from a video file using pydub.

    The three normalisation parameters match Whisper's expected input:
    mono, 16 kHz sample rate, 16-bit PCM. Doing this explicitly rather
    than letting Whisper normalise internally produces a smaller,
    faster-loading audio file.

    Args:
        video_fp: Path to the source video file.
        audio_fp: Destination path for the extracted audio.
            Parent directory must already exist.
        channels: Number of output channels. Defaults to 1 (mono).
        frame_rate: Output sample rate in Hz. Defaults to 16000.
        sample_width: Bytes per sample. 2 = 16-bit PCM.
        audio_format: Output format passed to pydub export.
            ``"wav"`` for local providers, ``"mp3"`` for OpenAI API.

    Returns:
        audio_fp (for chaining convenience).

    Raises:
        FileNotFoundError: If video_fp does not exist.
        ImportError: If pydub is not installed.
    """
    from pydub import AudioSegment  # noqa: PLC0415

    if not video_fp.exists():
        msg = f"Video file not found: {video_fp}"
        raise FileNotFoundError(msg)

    video_format = video_fp.suffix.lstrip(".").lower()
    lg.debug(f"Extracting audio: {video_fp} -> {audio_fp} ({audio_format})")

    video: AudioSegment = AudioSegment.from_file(video_fp, format=video_format)
    audio: AudioSegment = (
        video.set_channels(channels)
        .set_frame_rate(frame_rate)
        .set_sample_width(sample_width)
    )
    audio.export(audio_fp, format=audio_format)

    lg.debug(f"Audio extracted: {audio_fp} ({audio_fp.stat().st_size / 1024:.1f} KB)")
    return audio_fp


async def extract_audio_async(
    video_fp: Path,
    audio_fp: Path,
    *,
    channels: int = 1,
    frame_rate: int = 16_000,
    sample_width: int = 2,
    audio_format: str = "wav",
) -> Path:
    """Async wrapper: runs extract_audio in a thread pool.

    pydub wraps ffmpeg which is CPU/IO-bound. Running in asyncio.to_thread
    keeps the event loop free during extraction.

    Args:
        video_fp: Path to the source video file.
        audio_fp: Destination path for the extracted audio.
        channels: Number of output channels. Defaults to 1 (mono).
        frame_rate: Output sample rate in Hz. Defaults to 16000.
        sample_width: Bytes per sample. 2 = 16-bit PCM.
        audio_format: Output format passed to pydub export.

    Returns:
        audio_fp.
    """
    return await asyncio.to_thread(
        extract_audio,
        video_fp,
        audio_fp,
        channels=channels,
        frame_rate=frame_rate,
        sample_width=sample_width,
        audio_format=audio_format,
    )
