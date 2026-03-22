"""Test the media_downloader paths."""

from media_downloader.params.media_downloader_params import get_media_downloader_paths


def test_media_downloader_paths() -> None:
    """Test the media_downloader paths."""
    media_downloader_paths = get_media_downloader_paths()
    assert media_downloader_paths.src_fol.name == "media_downloader"
    assert media_downloader_paths.root_fol.name == "media-downloader"
    assert media_downloader_paths.data_fol.name == "data"
