"""Service configuration model for the media_downloader webapp."""

from media_downloader.data_models.basemodel_kwargs import BaseModelKwargs


class ServiceConfig(BaseModelKwargs):
    """Minimal webapp service configuration.

    Attributes:
        app_name:
            Application name shown in OpenAPI docs.
        app_version:
            Application version shown in OpenAPI docs.
        host:
            Server bind host.
        port:
            Server bind port.
        debug:
            Enable debug mode.
    """

    app_name: str = "Media Downloader API"
    app_version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
