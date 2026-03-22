"""FastAPI application factory for media_downloader."""

from fastapi import FastAPI
from fastapi_tools.routers.health import router as health_router

from media_downloader.params.media_downloader_params import get_webapp_params


def build_app() -> FastAPI:
    """Build the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    config = get_webapp_params().to_config()

    app = FastAPI(
        title=config.app_name,
        version=config.app_version,
        debug=config.debug,
    )
    app.state.config = config
    app.include_router(health_router)
    return app
