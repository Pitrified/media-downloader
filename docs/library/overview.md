# Using the Library

`media-downloader` can be used directly as a Python library without running any server. The core entry point is `DownloadRouter`, which detects the URL source, dispatches to the right provider, and runs any post-processing hooks (such as transcription).

## Installation

Install the extras you need alongside the core package:

```bash
# YouTube + TikTok only
uv sync --extra video

# All providers + local transcription
uv sync --all-extras
```

## Core concepts

URL detection:
`UrlDetector` classifies a URL into a `SourceType` (Instagram, YouTube, TikTok, web recipe) and extracts a platform-specific `source_id`.

Providers:
Each provider implements `BaseDownloader`, exposes `supported_sources`, and has `download()` / `adownload()` methods. Available providers: `InstaDownloader`, `YtDlpDownloader`, `WebRecipeDownloader`.

Storage:
`MediaStorage` manages the on-disk folder hierarchy. Downloads land in `{base_dir}/{source}/{source_id}/`.

Result:
Every download returns a `DownloadedMedia` dataclass with `video_file`, `thumbnail_file`, `audio_file`, `all_files`, `caption`, `metadata`, and an optional `transcription`.

## Minimal example

```python
from pathlib import Path
from media_downloader.core.router import DownloadRouter
from media_downloader.core.providers.yt_dlp import YtDlpDownloader
from media_downloader.storage.media_storage import MediaStorage

storage = MediaStorage(base_dir=Path("/tmp/media"))
router = DownloadRouter(downloaders=[YtDlpDownloader(storage=storage)])

media = router.download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

print(media.source.value)   # "youtube"
print(media.source_id)      # e.g. "dQw4w9WgXcQ"
print(media.video_file)     # Path to the downloaded .mp4
print(media.caption)        # Video description
```

## Async download

All providers support async via `adownload()`. Use it inside any async context:

```python
import asyncio

async def main() -> None:
    media = await router.adownload("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(media.all_files)

asyncio.run(main())
```

## Multiple providers

Pass multiple providers to the router. The detector picks the right one automatically:

```python
from media_downloader.core.providers.instagram import InstaDownloader
from media_downloader.core.providers.yt_dlp import YtDlpDownloader
from media_downloader.core.providers.web_recipe import WebRecipeDownloader

storage = MediaStorage(base_dir=Path("/tmp/media"))

router = DownloadRouter(
    downloaders=[
        YtDlpDownloader(storage=storage),
        InstaDownloader(storage=storage),
        WebRecipeDownloader(storage=storage),
    ]
)

# Each URL is automatically routed to the right provider
yt_media   = router.download("https://www.youtube.com/watch?v=...")
ig_media   = router.download("https://www.instagram.com/p/.../")
rec_media  = router.download("https://www.allrecipes.com/recipe/...")
```

## Working with DownloadedMedia

```python
media = router.download(url)

# Convenience properties
print(media.transcript)   # Full transcription text, or None
print(media.language)     # Detected language code, or None

# Files
print(media.video_file)       # Path | None
print(media.thumbnail_file)   # Path | None
print(media.audio_file)       # Path | None  (set by TranscriptionHook)
print(media.all_files)        # list[Path] - every file on disk

# Provider-specific metadata
# InstagramMetadata, YtDlpMetadata, WebRecipeMetadata, or None
print(media.metadata)
```

## Adding transcription

Transcription is added as a post-processing hook. First build a transcriber from `llm-core`, then wrap it in `TranscriptionHook`:

```python
from llm_core.transcription.providers.faster_whisper import FasterWhisperConfig
from llm_core.transcription.transcriber import create_transcriber
from media_downloader.post_processing.transcription import TranscriptionHook

transcriber = create_transcriber(FasterWhisperConfig(model="base", device="cpu"))

router = DownloadRouter(
    downloaders=[YtDlpDownloader(storage=storage)],
    post_processors=[TranscriptionHook(transcriber=transcriber)],
)

media = router.download("https://www.youtube.com/watch?v=...")
print(media.transcript)   # transcription text
print(media.language)     # e.g. "en"
```

## Audio extraction

If a provider downloads video but you want a standalone audio file for transcription, `TranscriptionHook` automatically extracts audio using `pydub` (which wraps `ffmpeg`). The extracted file is saved as a `.wav` sidecar alongside the video.

You can also extract audio manually:

```python
from media_downloader.post_processing.audio_extractor import extract_audio

audio_path = extract_audio(
    video_fp=media.video_file,
    audio_fp=Path("/tmp/audio.wav"),
    channels=1,
    frame_rate=16_000,
)
```

## Using DownloaderParams for full config

For production use, `DownloaderParams` loads the full configuration from environment variables. It is wired into `MediaDownloaderParams`:

```python
from media_downloader.params.load_env import load_env
from media_downloader.params.media_downloader_params import get_media_downloader_params

load_env()
params = get_media_downloader_params()
config = params.downloader.to_config()

print(config.db_path)
print(config.media_base_dir)
print(config.providers.video_enabled)
```

See [`DownloaderConfig`](../../reference/media_downloader/config/downloader_config/) and [`DownloaderParams`](../../reference/media_downloader/params/downloader_params/) in the API reference.
