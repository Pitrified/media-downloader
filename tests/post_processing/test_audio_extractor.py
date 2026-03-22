"""Tests for audio extraction utilities."""

from pathlib import Path

import pytest

from media_downloader.post_processing.audio_extractor import is_audio_file
from media_downloader.post_processing.audio_extractor import needs_extraction


class TestNeedsExtraction:
    """Tests for needs_extraction helper."""

    @pytest.mark.parametrize(
        "filename",
        ["video.mp4", "clip.webm", "movie.mkv", "footage.mov", "raw.avi", "stream.ts"],
    )
    def test_video_extensions_need_extraction(self, filename: str) -> None:
        """Known video extensions require extraction."""
        assert needs_extraction(Path(filename))

    @pytest.mark.parametrize(
        "filename",
        [
            "audio.mp3",
            "audio.wav",
            "audio.m4a",
            "audio.aac",
            "audio.ogg",
            "audio.flac",
        ],
    )
    def test_audio_extensions_no_extraction(self, filename: str) -> None:
        """Audio extensions do not need extraction."""
        assert not needs_extraction(Path(filename))

    def test_unknown_extension(self) -> None:
        """Unknown extension does not need extraction."""
        assert not needs_extraction(Path("readme.txt"))


class TestIsAudioFile:
    """Tests for is_audio_file helper."""

    @pytest.mark.parametrize(
        "filename",
        ["audio.mp3", "audio.wav", "audio.m4a", "audio.flac", "audio.ogg"],
    )
    def test_audio_files(self, filename: str) -> None:
        """Known audio extensions return True."""
        assert is_audio_file(Path(filename))

    def test_video_is_not_audio(self) -> None:
        """Video extension does not count as audio."""
        assert not is_audio_file(Path("video.mp4"))

    def test_unknown_is_not_audio(self) -> None:
        """Unknown extension is not audio."""
        assert not is_audio_file(Path("data.json"))
