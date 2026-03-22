# Media Downloader

Self-hosted media downloading service for a personal linux box. Downloads content from Instagram, YouTube/TikTok (via yt-dlp), and web recipes; optionally transcribes audio/video using local or API-based speech-to-text (via `llm-core`); and exposes a FastAPI HTTP API with a background worker queue.

## Installation

### Setup `uv`

To install the package:

Setup [`uv`](https://docs.astral.sh/uv/getting-started/installation/).

### Install the package

Run the following command:

```bash
uv sync --all-extras --all-groups
```

## Docs

Docs are available at [https://pitrified.github.io/media-downloader/](https://pitrified.github.io/media-downloader/).

## Setup

### Environment Variables

To setup the package, create a `.env` file in `~/cred/media-downloader/.env` with the following content (see `nokeys.env` for the full list):

```bash
MEDIA_DOWNLOADER_SAMPLE_ENV_VAR=sample
```

And for VSCode to recognize the environment file, add the following line to the workspace [settings file](.vscode/settings.json):

```json
"python.envFile": "/home/pmn/cred/media-downloader/.env"
```

Note that the path to the `.env` file should be absolute.

### Pre-commit

To install the pre-commit hooks, run the following command:

```bash
pre-commit install
```

### Linting

```bash
uv run pyright
uv run ruff check --fix
uv run ruff format
```

### Testing

```bash
uv run pytest
```
