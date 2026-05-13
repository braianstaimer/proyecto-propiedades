from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator
from datetime import date

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_USER", "appuser")
os.environ.setdefault("DB_PASSWORD", "apppass")
os.environ.setdefault("DB_NAME", "propiedades_db")
os.environ.setdefault("OLLAMA_URL", "http://localhost:11434")
os.environ.setdefault("MOCK_LLM", "true")

from app.config import get_settings  # noqa: E402
from app.llm_service import MockLLMProvider  # noqa: E402
from app.repositories import InMemoryPropertyRepository, PropertyRow  # noqa: E402

SAMPLE_ROWS: list[PropertyRow] = [
    PropertyRow(
        id=1,
        titulo="Casa moderna en Zona 10",
        descripcion="Acabados de lujo.",
        tipo="casa",
        precio=320000.0,
        habitaciones=3,
        banos=3,
        area_m2=240.0,
        ubicacion="Zona 10, Guatemala",
        fecha_publicacion=date(2026, 4, 21),
    ),
    PropertyRow(
        id=2,
        titulo="Apartamento Zona 15",
        descripcion="Ubicación residencial tranquila.",
        tipo="departamento",
        precio=132000.0,
        habitaciones=2,
        banos=2,
        area_m2=88.0,
        ubicacion="Zona 15, Guatemala",
        fecha_publicacion=date(2026, 4, 29),
    ),
]


@pytest.fixture(autouse=True)
def reset_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def mock_llm() -> MockLLMProvider:
    return MockLLMProvider()


@pytest.fixture
def in_memory_repo() -> InMemoryPropertyRepository:
    return InMemoryPropertyRepository(SAMPLE_ROWS)


@pytest.fixture
def integration_client() -> Iterator[TestClient]:
    """TestClient real contra MySQL local. Skip si MySQL no responde."""
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        if sock.connect_ex(("localhost", 3306)) != 0:
            pytest.skip("MySQL no disponible en localhost:3306")
    finally:
        sock.close()

    from app.main import app

    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture
async def in_memory_app_client() -> AsyncIterator[TestClient]:
    """Cliente FastAPI cuya repo es in-memory (sin MySQL)."""
    from app.dependencies import get_property_repository
    from app.main import app

    app.dependency_overrides[get_property_repository] = lambda: InMemoryPropertyRepository(
        SAMPLE_ROWS
    )

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(get_property_repository, None)
