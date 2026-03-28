"""Pytest configuration and shared fixtures."""

import os

from media_downloader.params.load_env import load_env

# Stub values for CI environments where ~/cred/media-downloader/.env is absent.
# These are set BEFORE load_env() so that load_dotenv (which does not
# override by default) leaves them untouched even when the real .env exists.
os.environ.setdefault("SAMPLE_API_KEY", "test-api-key-do-not-use-in-prod")
os.environ.setdefault("MEDIA_DOWNLOADER_SAMPLE_ENV_VAR", "sample")

load_env()
