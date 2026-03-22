"""Shared test fixtures for webapp tests."""

from collections.abc import Generator

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from media_downloader.metaclasses.singleton import Singleton
from media_downloader.webapp.main import build_app


@pytest.fixture(autouse=True)
def reset_singleton() -> Generator[None]:
    """Reset the MediaDownloaderParams singleton between tests."""
    yield
    Singleton._instances.clear()  # noqa: SLF001


@pytest.fixture
def app() -> FastAPI:
    """Create test FastAPI application."""
    return build_app()


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient]:
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client
