"""Cross-implementation contract tests for PropertyRepository (LSP)."""
from __future__ import annotations

from datetime import date

import pytest

from app.repositories import InMemoryPropertyRepository, PropertyRepository, PropertyRow
from app.sql_validator import ValidatedSQL

SAMPLE = PropertyRow(
    id=1,
    titulo="t",
    descripcion="d",
    tipo="casa",
    precio=1.0,
    habitaciones=1,
    banos=1,
    area_m2=1.0,
    ubicacion="x",
    fecha_publicacion=date(2026, 1, 1),
)


REPO_FACTORIES = [
    pytest.param(lambda: InMemoryPropertyRepository([SAMPLE]), id="in-memory"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("factory", REPO_FACTORIES)
async def test_execute_validated_select_returns_sequence(factory) -> None:
    repo: PropertyRepository = factory()
    rows = await repo.execute_validated_select(ValidatedSQL("SELECT 1 FROM propiedades LIMIT 1"))
    assert all(isinstance(r, PropertyRow) for r in rows)


@pytest.mark.asyncio
@pytest.mark.parametrize("factory", REPO_FACTORIES)
async def test_healthcheck_bool(factory) -> None:
    repo: PropertyRepository = factory()
    assert isinstance(await repo.healthcheck(), bool)
