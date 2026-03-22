"""Test that the environment variables are available."""

import os


def test_env_vars() -> None:
    """The environment var MEDIA_DOWNLOADER_SAMPLE_ENV_VAR is available."""
    assert "MEDIA_DOWNLOADER_SAMPLE_ENV_VAR" in os.environ
    assert os.environ["MEDIA_DOWNLOADER_SAMPLE_ENV_VAR"] == "sample"
