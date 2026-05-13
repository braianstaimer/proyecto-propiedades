from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.exceptions import DatabaseError
from app.repositories import (
    InMemoryPropertyRepository,
    MySQLPropertyRepository,
    PropertyRow,
)
from app.sql_validator import ValidatedSQL

SAMPLE = PropertyRow(
    id=1,
    titulo="t",
    descripcion=None,
    tipo="casa",
    precio=1.0,
    habitaciones=None,
    banos=None,
    area_m2=None,
    ubicacion="x",
    fecha_publicacion=date(2026, 1, 1),
)


@pytest.mark.asyncio
async def test_in_memory_returns_rows() -> None:
    repo = InMemoryPropertyRepository([SAMPLE])
    rows = await repo.execute_validated_select(ValidatedSQL("SELECT 1 FROM propiedades"))
    assert len(rows) == 1
    assert rows[0].titulo == "t"


@pytest.mark.asyncio
async def test_in_memory_healthcheck_true() -> None:
    assert await InMemoryPropertyRepository([]).healthcheck() is True


def test_property_row_from_mapping_handles_decimal_and_str_date() -> None:
    mapping = {
        "id": 1,
        "titulo": "T",
        "descripcion": "D",
        "tipo": "casa",
        "precio": Decimal("123.45"),
        "habitaciones": 3,
        "banos": 2,
        "area_m2": Decimal("80.5"),
        "ubicacion": "X",
        "fecha_publicacion": "2026-04-21",
    }
    row = PropertyRow.from_mapping(mapping)
    assert row.precio == 123.45
    assert row.area_m2 == 80.5
    assert row.fecha_publicacion == date(2026, 4, 21)


def test_property_row_from_mapping_nulls() -> None:
    mapping = {
        "id": 1,
        "titulo": "T",
        "descripcion": None,
        "tipo": "terreno",
        "precio": 0,
        "habitaciones": None,
        "banos": None,
        "area_m2": None,
        "ubicacion": "X",
        "fecha_publicacion": date(2026, 1, 1),
    }
    row = PropertyRow.from_mapping(mapping)
    assert row.habitaciones is None
    assert row.banos is None
    assert row.area_m2 is None


class _FakeDataSource:
    def __init__(self, *, raise_on_execute: type[Exception] | None = None) -> None:
        self._raise = raise_on_execute

    def session(self):
        raise_cls = self._raise

        @asynccontextmanager
        async def cm():
            class _Sess:
                async def execute(self, *_args, **_kwargs):
                    if raise_cls is not None:
                        if raise_cls is OperationalError:
                            raise OperationalError("stmt", {}, Exception("MySQL down"))
                        raise raise_cls("boom")

                    class _R:
                        def __iter__(self):
                            return iter([])

                    return _R()

            yield _Sess()

        return cm()

    async def healthcheck(self) -> bool:
        return self._raise is None

    async def close(self) -> None: ...


@pytest.mark.asyncio
async def test_mysql_repo_wraps_operational_error() -> None:
    repo = MySQLPropertyRepository(_FakeDataSource(raise_on_execute=OperationalError))  # type: ignore[arg-type]
    with pytest.raises(DatabaseError):
        await repo.execute_validated_select(ValidatedSQL("SELECT id FROM propiedades"))


@pytest.mark.asyncio
async def test_mysql_repo_wraps_sqlalchemy_error() -> None:
    repo = MySQLPropertyRepository(_FakeDataSource(raise_on_execute=SQLAlchemyError))  # type: ignore[arg-type]
    with pytest.raises(DatabaseError):
        await repo.execute_validated_select(ValidatedSQL("SELECT id FROM propiedades"))


@pytest.mark.asyncio
async def test_mysql_repo_healthcheck_delegates() -> None:
    repo = MySQLPropertyRepository(_FakeDataSource())  # type: ignore[arg-type]
    assert await repo.healthcheck() is True
