# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.2] - 2026-03-30

### Changed

- Removed automatic `load_env()` call from `media_downloader/__init__.py`; callers are
  now responsible for loading environment variables before importing params.
- Moved `load_env()` into `tests/conftest.py` so tests continue to pick up
  `~/cred/media-downloader/.env` without relying on package-level side effects.
- Bumped `llm-core` dependency from `v0.2.0` to `v0.2.1` across all extras
  (`stt-local`, `stt-api`, `faster-whisper`, and the base dep).

### Added

- `docs/guides/env_loading.md` - guide explaining the environment loading
  pattern and how to call `load_env()` correctly from application code.

---

## [0.1.1] - 2026-03-27

### Fixed

- Added `[tool.hatch.metadata] allow-direct-references = true` so hatchling accepts direct
  URL references to internal git-tag dependencies at build time.

---

## [0.1.0] - 2026-03-23

Initial release. Self-hosted media downloading service for Instagram, YouTube/TikTok, web
recipes, and general web pages; with optional transcription via `llm-core` and a FastAPI HTTP
API backed by a background worker queue.

### Added

**Core**
- `DownloadedMedia` - common result type for all downloaders.
- `BaseDownloader` - abstract base with shared logic.
- `UrlDetector` - classifies URLs to choose the right downloader.
- `DownloadRouter` - dispatches to the correct provider.

**Providers**
- `InstaDownloader` - Instagram posts and reels via instaloader.
- `YtDlpDownloader` - YouTube, TikTok, and any yt-dlp-supported site.
- `WebRecipeDownloader` - structured recipe extraction via recipe-scrapers + trafilatura.

**Post-processing**
- `TranscriptionHook` - pluggable hook interface for post-download transcription.
- `AudioExtractor` - extracts audio from video files.

**Storage**
- `MediaStorage` - folder hierarchy and path construction for downloaded media.

**Database**
- SQLAlchemy ORM models for download records.
- `DownloadDBService` - async CRUD service.
- Alembic migration baseline.

**Webapp**
- FastAPI app factory in `src/media_downloader/webapp/main.py`.
- Health router, background worker, and job-queue router.
- Entry point for uvicorn: `media_downloader.webapp.app:app`.

**Config / Params pattern**
- `BaseModelKwargs` - Pydantic base with `to_kw(exclude_none=True)` kwargs flattening.
- `Singleton` metaclass - one instance per process, reset-able in tests.
- `EnvType` + `EnvStageType` / `EnvLocationType` enums.
- `MediaDownloaderParams` singleton + `MediaDownloaderPaths`.
- `load_env()` - loads `~/cred/media-downloader/.env` via python-dotenv.
