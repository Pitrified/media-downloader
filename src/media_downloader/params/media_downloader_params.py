"""MediaDownloader project params.

Parameters are actual value of the config.

The class is a singleton, so it can be accessed from anywhere in the code.

There is a parameter regarding the environment type (stage and location), which
is used to load different paths and other parameters based on the environment.
"""

from loguru import logger as lg

from media_downloader.metaclasses.singleton import Singleton
from media_downloader.params.env_type import EnvType
from media_downloader.params.media_downloader_paths import MediaDownloaderPaths
from media_downloader.params.sample_params import SampleParams
from media_downloader.params.webapp import WebappParams


class MediaDownloaderParams(metaclass=Singleton):
    """MediaDownloader project parameters."""

    def __init__(self) -> None:
        """Load the MediaDownloader params."""
        lg.info("Loading MediaDownloader params")
        self.set_env_type()

    def set_env_type(self, env_type: EnvType | None = None) -> None:
        """Set the environment type.

        Args:
            env_type (EnvType | None): The environment type.
                If None, it will be set from the environment variables.
                Defaults to None.
        """
        if env_type is not None:
            self.env_type = env_type
        else:
            self.env_type = EnvType.from_env_var()
        self.load_config()

    def load_config(self) -> None:
        """Load the media_downloader configuration."""
        self.paths = MediaDownloaderPaths(env_type=self.env_type)
        self.sample = SampleParams()
        self.webapp = WebappParams(
            stage=self.env_type.stage,
            location=self.env_type.location,
        )

    def __str__(self) -> str:
        """Return the string representation of the object."""
        s = "MediaDownloaderParams:"
        s += f"\n{self.paths}"
        s += f"\n{self.sample}"
        s += f"\n{self.webapp}"
        return s

    def __repr__(self) -> str:
        """Return the string representation of the object."""
        return str(self)


def get_media_downloader_params() -> MediaDownloaderParams:
    """Get the media_downloader params."""
    return MediaDownloaderParams()


def get_media_downloader_paths() -> MediaDownloaderPaths:
    """Get the media_downloader paths."""
    return get_media_downloader_params().paths


def get_webapp_params() -> WebappParams:
    """Get the webapp params."""
    return get_media_downloader_params().webapp
