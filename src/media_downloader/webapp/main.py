"""FastAPI application factory for media_downloader."""

from fastapi import FastAPI
from fastapi_tools.routers.health import router as health_router

from media_downloader.params.media_downloader_params import get_downloader_params
from media_downloader.params.media_downloader_params import get_webapp_params
from media_downloader.webapp.lifespan import lifespan
from media_downloader.webapp.routers.queue_router import router as queue_router
from media_downloader.webapp.routers.sync_router import router as sync_router


def build_app() -> FastAPI:
    """Build the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    config = get_webapp_params().to_config()
    dl_config = get_downloader_params().to_config()

    app = FastAPI(
        title=config.app_name,
        version=config.app_version,
        debug=config.debug,
        lifespan=lifespan,
    )
    app.state.config = config
    app.state.downloader_config = dl_config

    app.include_router(health_router)
    app.include_router(sync_router)
    app.include_router(queue_router)

    return app
