from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from docent.api.main import create_app
from docent.config import get_settings


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("APP_ENV", "test")
    get_settings.cache_clear()
    with TestClient(create_app()) as c:
        yield c
    get_settings.cache_clear()
