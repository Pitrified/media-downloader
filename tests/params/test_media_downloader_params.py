"""Test the MediaDownloaderParams class."""

from media_downloader.params.media_downloader_params import MediaDownloaderParams
from media_downloader.params.media_downloader_params import get_media_downloader_params
from media_downloader.params.media_downloader_paths import MediaDownloaderPaths
from media_downloader.params.sample_params import SampleParams


def test_media_downloader_params_singleton() -> None:
    """Test that MediaDownloaderParams is a singleton."""
    params1 = MediaDownloaderParams()
    params2 = MediaDownloaderParams()
    assert params1 is params2
    assert get_media_downloader_params() is params1


def test_media_downloader_params_init() -> None:
    """Test initialization of MediaDownloaderParams."""
    params = MediaDownloaderParams()
    assert isinstance(params.paths, MediaDownloaderPaths)
    assert isinstance(params.sample, SampleParams)


def test_media_downloader_params_str() -> None:
    """Test string representation."""
    params = MediaDownloaderParams()
    s = str(params)
    assert "MediaDownloaderParams:" in s
    assert "MediaDownloaderPaths:" in s
    assert "SampleParams:" in s
