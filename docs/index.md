# Media Downloader

Self-hosted media downloading service for a personal linux box.

Downloads content from Instagram, YouTube/TikTok (via yt-dlp), and web recipes; optionally transcribes audio/video using local or API-based speech-to-text (via `llm-core`); and exposes a FastAPI HTTP API with a background worker queue.

## Features

- **Instagram**: Download posts, reels, and stories via `instaloader`
- **YouTube/TikTok**: Download video and audio via `yt-dlp`
- **Web recipes**: Scrape recipe pages via `recipe-scrapers` and `trafilatura`
- **Transcription**: Optional speech-to-text via `llm-core` (local Whisper or OpenAI API)
- **HTTP API**: FastAPI service with a background job queue

## Quick Start

```bash
# Install dependencies
uv sync --all-extras --all-groups

# Set up credentials
cp nokeys.env ~/cred/media-downloader/.env
# edit ~/cred/media-downloader/.env with real values

# Run tests
uv run pytest

# Start the API server
uvicorn media_downloader.webapp.app:app --reload
```

## Project Structure

```
media-downloader/
├── src/media_downloader/
│   ├── core/           # DownloadedMedia, providers, router
│   ├── post_processing/ # TranscriptionHook, AudioExtractor
│   ├── storage/        # MediaStorage
│   ├── db/             # SQLAlchemy models, DownloadDBService
│   ├── config/         # Pydantic settings models
│   ├── params/         # Runtime value loading
│   └── webapp/         # FastAPI app, worker, routers
├── tests/
├── docs/
└── scratch_space/
```

## Next Steps

- [Getting Started](getting-started.md) - Set up your development environment
- [Guides](guides/uv.md) - Learn about the tools used in this project
- [API Reference](reference/) - Explore the codebase
- [Contributing](contributing.md) - How to contribute to this project
