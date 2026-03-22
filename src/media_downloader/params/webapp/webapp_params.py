"""Webapp parameters with environment-aware loading.

Parameters are actual values loaded from environment variables.
Supports ENV_STAGE_TYPE (dev/prod) and ENV_LOCATION_TYPE (local/render).
"""

import os

from loguru import logger as lg

from media_downloader.config.service_config import ServiceConfig
from media_downloader.params.env_type import EnvLocationType
from media_downloader.params.env_type import EnvStageType


class WebappParams:
    """Webapp parameters loaded from environment variables."""

    def __init__(
        self,
        stage: EnvStageType | None = None,
        location: EnvLocationType | None = None,
    ) -> None:
        """Load webapp params from environment.

        Args:
            stage: Environment stage (dev/prod). Loaded from env if None.
            location: Environment location (local/render). Loaded from env if None.
        """
        lg.info("Loading WebappParams")

        self.stage = stage or EnvStageType.from_env_var()
        self.location = location or EnvLocationType.from_env_var()

        self._load_params()

    def _load_params(self) -> None:
        """Load all parameters from environment."""
        self.host: str = os.getenv("WEBAPP_HOST", "127.0.0.1")
        self.port: int = int(os.getenv("WEBAPP_PORT", "8000"))
        self.debug: bool = os.getenv("WEBAPP_DEBUG", "false").lower() == "true"
        self.app_name: str = "Media Downloader API"
        self.app_version: str = "0.1.0"

    def to_config(self) -> ServiceConfig:
        """Assemble and return the service configuration.

        Returns:
            ServiceConfig instance.
        """
        return ServiceConfig(
            app_name=self.app_name,
            app_version=self.app_version,
            host=self.host,
            port=self.port,
            debug=self.debug,
        )

    def __str__(self) -> str:
        """Return string representation."""
        return f"WebappParams(host={self.host}, port={self.port}, debug={self.debug})"

    def __repr__(self) -> str:
        """Return string representation."""
        return str(self)
