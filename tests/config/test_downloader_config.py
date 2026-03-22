"""Tests for downloader configuration."""

from pathlib import Path

from media_downloader.config.downloader_config import DownloaderConfig
from media_downloader.config.downloader_config import ProvidersConfig


def test_providers_config_defaults() -> None:
    """ProvidersConfig has sensible defaults."""
    config = ProvidersConfig()
    assert config.instagram_enabled is True
    assert config.video_enabled is True
    assert config.web_recipe_enabled is True
    assert config.transcription is None


def test_downloader_config_creation(tmp_path: Path) -> None:
    """DownloaderConfig can be created with required fields."""
    config = DownloaderConfig(
        db_path=tmp_path / "test.db",
        media_base_dir=tmp_path / "media",
    )
    assert config.db_path == tmp_path / "test.db"
    assert config.media_base_dir == tmp_path / "media"
    assert config.providers.instagram_enabled is True
    assert config.log_level == "INFO"
