"""Tests for MediaStorage."""

from pathlib import Path

from media_downloader.core.models import SourceType
from media_downloader.storage.media_storage import MediaStorage


def test_source_dir_created(tmp_path: Path) -> None:
    """source_dir creates directory structure."""
    storage = MediaStorage(base_dir=tmp_path)
    d = storage.source_dir(SourceType.INSTAGRAM, "abc123")
    assert d.exists()
    assert d == tmp_path / "instagram" / "abc123"


def test_media_path_returns_correct_path(tmp_path: Path) -> None:
    """media_path builds correct file path."""
    storage = MediaStorage(base_dir=tmp_path)
    fp = storage.media_path(
        SourceType.YOUTUBE,
        "vid1",
        role="video",
        ext="mp4",
    )
    assert fp == tmp_path / "youtube" / "vid1" / "video.mp4"
    assert fp.parent.exists()


def test_media_path_audio_sidecar(tmp_path: Path) -> None:
    """media_path builds audio sidecar path correctly."""
    storage = MediaStorage(base_dir=tmp_path)
    fp = storage.media_path(
        SourceType.INSTAGRAM,
        "post1",
        role="audio",
        ext="wav",
    )
    assert fp == tmp_path / "instagram" / "post1" / "audio.wav"


def test_list_files_empty(tmp_path: Path) -> None:
    """list_files returns empty list for non-existent directory."""
    storage = MediaStorage(base_dir=tmp_path)
    assert storage.list_files(SourceType.YOUTUBE, "nope") == []


def test_list_files_with_files(tmp_path: Path) -> None:
    """list_files returns sorted file paths."""
    storage = MediaStorage(base_dir=tmp_path)
    d = storage.source_dir(SourceType.YOUTUBE, "vid1")
    (d / "video.mp4").touch()
    (d / "audio.wav").touch()
    files = storage.list_files(SourceType.YOUTUBE, "vid1")
    assert len(files) == 2
    assert files[0].name == "audio.wav"
    assert files[1].name == "video.mp4"


def test_cleanup_removes_files(tmp_path: Path) -> None:
    """Cleanup removes files but keeps directory."""
    storage = MediaStorage(base_dir=tmp_path)
    d = storage.source_dir(SourceType.YOUTUBE, "vid1")
    (d / "video.mp4").touch()
    (d / "audio.wav").touch()
    storage.cleanup(SourceType.YOUTUBE, "vid1")
    assert d.exists()
    assert storage.list_files(SourceType.YOUTUBE, "vid1") == []
