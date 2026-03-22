"""Application instance for uvicorn.

Entry point: uvicorn media_downloader.webapp.app:app
"""

from media_downloader.webapp.main import build_app

# Create application instance
app = build_app()

if __name__ == "__main__":
    import uvicorn

    from media_downloader.params.media_downloader_params import get_webapp_params

    params = get_webapp_params()
    uvicorn.run(
        "media_downloader.webapp.app:app",
        host=params.host,
        port=params.port,
        reload=params.debug,
    )
