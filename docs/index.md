# Media Downloader

A self-hosted media downloading service for a personal Linux box. Point it at a URL and it fetches the content, organises it on disk, and optionally transcribes the audio - either through a Python library call or an HTTP API.

## What it does

`media-downloader` supports three kinds of content:

- **Instagram** - posts, reels, and stories downloaded via `instaloader`
- **YouTube and TikTok** - video/audio via `yt-dlp`, with format control
- **Web recipes** - structured recipe data scraped via `recipe-scrapers` and `trafilatura`

Optionally, downloaded audio and video can be passed through a speech-to-text pipeline powered by [`llm-core`](https://github.com/Pitrified/llm-core), supporting local Whisper models, faster-whisper, or the OpenAI API.

## Two ways to use it

**As a Python library** - import `DownloadRouter`, give it a URL, and get back a `DownloadedMedia` dataclass with file paths, caption, and optional transcription. No server required.

**As an HTTP API** - run the FastAPI server and call `POST /download` for a synchronous result or `POST /jobs` to submit to the background queue and poll `GET /jobs/{id}`.

See [Using the Library](library/overview.md) or [Using the HTTP API](library/http-api.md) for practical examples.

## Quick start

```bash
# Install all extras (providers + transcription)
uv sync --all-extras --all-groups

# Copy the credentials template and fill in real values
cp nokeys.env ~/cred/media-downloader/.env

# Run the test suite
uv run pytest

# Start the API server (auto-reload for development)
uvicorn media_downloader.webapp.app:app --reload
```

The server starts on `http://localhost:8000`. Visit `/docs` for the interactive Swagger UI.

## Project layout

```
media-downloader/
├── src/media_downloader/
│   ├── core/            # UrlDetector, DownloadRouter, DownloadedMedia, providers
│   ├── post_processing/ # TranscriptionHook, audio extraction
│   ├── storage/         # MediaStorage - on-disk directory hierarchy
│   ├── db/              # SQLAlchemy ORM, DownloadDBService
│   ├── config/          # Pydantic config shapes (DownloaderConfig, ProvidersConfig)
│   ├── params/          # Environment-aware value loading
│   └── webapp/          # FastAPI app, routers, worker, lifespan
```

## Optional dependency groups

| Extra | Installs |
|-------|----------|
| `instagram` | instaloader |
| `video` | yt-dlp |
| `recipe` | recipe-scrapers, trafilatura |
| `stt-local` | openai-whisper |
| `stt-local-fast` | faster-whisper |
| `stt-api` | OpenAI API client |
| `webapp` | FastAPI, uvicorn |
| `all` | everything above |

Install only what you need:

```bash
uv sync --extra video --extra webapp
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
