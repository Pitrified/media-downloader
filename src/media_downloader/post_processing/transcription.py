"""Transcription post-processor.

``TranscriptionHook`` extracts audio from video if needed, then delegates
to a ``BaseTranscriber`` from ``llm-core``. It is the only post-processor
that bridges the download pipeline to the transcription subsystem.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from loguru import logger as lg

from media_downloader.post_processing.audio_extractor import extract_audio_async
from media_downloader.post_processing.audio_extractor import needs_extraction

if TYPE_CHECKING:
    from pathlib import Path

    from llm_core.transcription.base import BaseTranscriber

    from media_downloader.core.models import DownloadedMedia
    from media_downloader.storage.media_storage import MediaStorage


class TranscriptionHook:
    """Post-processor: extracts audio if needed, then transcribes.

    Audio extraction and transcription are both CPU/IO-bound and run via
    asyncio.to_thread internally. The hook's public API is async-first.

    Attributes:
        _transcriber:
            A ``BaseTranscriber`` instance from llm-core.
        _storage:
            Media storage for resolving the audio sidecar path.
        _audio_format:
            Extraction format (``"wav"`` for local, ``"mp3"`` for API).
    """

    def __init__(
        self,
        transcriber: BaseTranscriber,
        storage: MediaStorage,
        audio_format: str = "wav",
    ) -> None:
        """Initialize the transcription hook.

        Args:
            transcriber: A ``BaseTranscriber`` instance, created once at
                service startup via ``create_transcriber()``.
            storage: ``MediaStorage`` instance for resolving the audio
                sidecar path.
            audio_format: Extraction format. ``"wav"`` for local providers
                (default), ``"mp3"`` for OpenAI API to reduce upload size.
        """
        self._transcriber = transcriber
        self._storage = storage
        self._audio_format = audio_format

    async def aprocess(self, media: DownloadedMedia) -> DownloadedMedia:
        """Extract audio if needed, transcribe, populate media.transcription.

        Skips gracefully if no video or audio file is present.
        Reuses an existing audio sidecar if already extracted.

        Args:
            media: ``DownloadedMedia`` to enrich in-place.

        Returns:
            The same ``DownloadedMedia`` instance with transcription populated.
        """
        audio_fp = await self._resolve_audio(media)
        if audio_fp is None:
            lg.debug(
                f"No audio available for {media.source_id}, skipping transcription",
            )
            return media

        lg.info(f"Transcribing {audio_fp} via {self._transcriber.provider_name}")
        media.transcription = await self._transcriber.atranscribe(audio_fp)
        lg.info(
            f"Transcription done: {len(media.transcription.text)} chars, "
            f"language={media.transcription.language}",
        )
        return media

    def process(self, media: DownloadedMedia) -> DownloadedMedia:
        """Sync variant. Runs aprocess in a new event loop.

        Prefer ``aprocess`` in async contexts. This is provided for
        compatibility with the sync ``PostProcessor`` protocol.

        Args:
            media: ``DownloadedMedia`` to enrich.

        Returns:
            Enriched ``DownloadedMedia``.
        """
        return asyncio.run(self.aprocess(media))

    async def _resolve_audio(self, media: DownloadedMedia) -> Path | None:
        """Return the audio file path, extracting from video if necessary.

        Resolution order:
            1. ``media.audio_file`` - already an audio file, use directly
            2. Existing audio sidecar in MediaStorage - skip re-extraction
            3. ``media.video_file`` - extract audio, persist sidecar
            4. ``None`` - no audio source available

        Args:
            media: The downloaded media to resolve audio for.

        Returns:
            Path to an audio file, or None if unavailable.
        """
        # Already have a dedicated audio file
        if media.audio_file is not None:
            return media.audio_file

        # Determine sidecar path
        sidecar_fp = self._storage.media_path(
            media.source,
            media.source_id,
            role="audio",
            ext=self._audio_format,
        )

        # Reuse existing sidecar
        if sidecar_fp.exists():
            lg.debug(f"Reusing existing audio sidecar: {sidecar_fp}")
            return sidecar_fp

        # Extract from video
        if media.video_file is not None and needs_extraction(media.video_file):
            await extract_audio_async(
                media.video_file,
                sidecar_fp,
                audio_format=self._audio_format,
            )
            # Register sidecar in media's file list so DB layer persists it
            media.all_files.append(sidecar_fp)
            media.audio_file = sidecar_fp
            return sidecar_fp

        return None
