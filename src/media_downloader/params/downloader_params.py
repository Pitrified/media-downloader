"""Downloader parameters with environment-aware loading.

Loads actual values for the download service configuration and assembles
a ``DownloaderConfig``. Transcription provider selection is dispatched
by environment stage/location.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger as lg

from media_downloader.config.downloader_config import DownloaderConfig
from media_downloader.config.downloader_config import ProvidersConfig
from media_downloader.params.env_type import EnvLocationType
from media_downloader.params.env_type import EnvStageType
from media_downloader.params.env_type import EnvType
from media_downloader.params.env_type import UnknownEnvLocationError
from media_downloader.params.env_type import UnknownEnvStageError

if TYPE_CHECKING:
    from media_downloader.params.media_downloader_paths import MediaDownloaderPaths


class DownloaderParams:
    """Parameters for the download service.

    Loads provider configuration and transcription backend selection
    based on the deployment environment.
    """

    def __init__(
        self,
        paths: MediaDownloaderPaths,
        env_type: EnvType | None = None,
    ) -> None:
        """Load downloader params.

        Args:
            paths: Resolved project paths.
            env_type: Deployment environment. Read from env vars if None.
        """
        lg.info("Loading DownloaderParams")
        self._paths = paths
        self.env_type = env_type or EnvType.from_env_var()
        self._load_params()

    def _load_params(self) -> None:
        """Dispatch loading by stage and location."""
        self._load_common_params()
        match self.env_type.stage:
            case EnvStageType.DEV:
                self._load_dev_params()
            case EnvStageType.PROD:
                self._load_prod_params()
            case _:
                raise UnknownEnvStageError(self.env_type.stage)

    def _load_common_params(self) -> None:
        """Load params shared across all environments."""
        self.db_path = self._paths.data_fol / "downloads.db"
        self.media_base_dir = self._paths.data_fol / "media"
        self.yt_dlp_format = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        self.instagram_enabled = True
        self.video_enabled = True
        self.web_recipe_enabled = True
        self.transcription_config = None

    def _load_dev_params(self) -> None:
        """Load dev-stage params."""
        match self.env_type.location:
            case EnvLocationType.LOCAL:
                self._load_dev_local_params()
            case EnvLocationType.RENDER:
                self._load_dev_render_params()
            case _:
                raise UnknownEnvLocationError(self.env_type.location)

    def _load_prod_params(self) -> None:
        """Load prod-stage params."""
        match self.env_type.location:
            case EnvLocationType.LOCAL:
                self._load_prod_local_params()
            case EnvLocationType.RENDER:
                self._load_prod_render_params()
            case _:
                raise UnknownEnvLocationError(self.env_type.location)

    def _load_dev_local_params(self) -> None:
        """Dev + local: transcription disabled for fast iteration."""

    def _load_dev_render_params(self) -> None:
        """Dev + render: transcription disabled."""

    def _load_prod_local_params(self) -> None:
        """Prod + local (linux box): faster-whisper medium on CPU."""
        try:
            from llm_core.transcription.config.faster_whisper import (  # noqa: PLC0415
                FasterWhisperConfig,
            )

            self.transcription_config = FasterWhisperConfig(
                model="medium",
                device="cpu",
            )
        except ImportError:
            lg.warning(
                "llm-core[faster-whisper] not installed, transcription disabled",
            )

    def _load_prod_render_params(self) -> None:
        """Prod + render: transcription disabled (no GPU on Render)."""

    def to_config(self) -> DownloaderConfig:
        """Assemble the downloader configuration.

        Returns:
            Populated ``DownloaderConfig`` instance.
        """
        providers = ProvidersConfig(
            instagram_enabled=self.instagram_enabled,
            video_enabled=self.video_enabled,
            web_recipe_enabled=self.web_recipe_enabled,
            transcription=self.transcription_config,
        )
        return DownloaderConfig(
            db_path=self.db_path,
            media_base_dir=self.media_base_dir,
            providers=providers,
            yt_dlp_format=self.yt_dlp_format,
        )

    def __str__(self) -> str:
        """Return string representation."""
        transcription_str = (
            type(self.transcription_config).__name__
            if self.transcription_config
            else "disabled"
        )
        return (
            f"DownloaderParams("
            f"db_path={self.db_path}, "
            f"media_base_dir={self.media_base_dir}, "
            f"transcription={transcription_str})"
        )

    def __repr__(self) -> str:
        """Return string representation."""
        return str(self)
