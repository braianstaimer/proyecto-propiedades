from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.config import Settings
from app.database import DataSource
from app.exceptions import DatabaseError
from app.sql_validator import ValidatedSQL


@dataclass(frozen=True)
class PropertyRow:
    id: int
    titulo: str
    descripcion: str | None
    tipo: str
    precio: float
    habitaciones: int | None
    banos: int | None
    area_m2: float | None
    ubicacion: str
    fecha_publicacion: date

    @classmethod
    def from_mapping(cls, mapping: dict) -> PropertyRow:
        return cls(
            id=int(mapping["id"]),
            titulo=str(mapping["titulo"]),
            descripcion=mapping.get("descripcion"),
            tipo=str(mapping["tipo"]),
            precio=_to_float(mapping["precio"]),
            habitaciones=_optional_int(mapping.get("habitaciones")),
            banos=_optional_int(mapping.get("banos")),
            area_m2=_optional_float(mapping.get("area_m2")),
            ubicacion=str(mapping["ubicacion"]),
            fecha_publicacion=_to_date(mapping["fecha_publicacion"]),
        )


def _to_float(value: object) -> float:
    if isinstance(value, Decimal | int | float):
        return float(value)
    return float(str(value))


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    return int(str(value))


def _optional_float(value: object) -> float | None:
    return None if value is None else _to_float(value)


def _to_date(value: object) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


class PropertyRepository(ABC):
    @abstractmethod
    async def execute_validated_select(
        self, validated_sql: ValidatedSQL
    ) -> Sequence[PropertyRow]: ...

    @abstractmethod
    async def healthcheck(self) -> bool: ...


class MySQLPropertyRepository(PropertyRepository):
    def __init__(self, datasource: DataSource) -> None:
        self._datasource = datasource

    async def execute_validated_select(
        self, validated_sql: ValidatedSQL
    ) -> Sequence[PropertyRow]:
        try:
            async with self._datasource.session() as session:
                result = await session.execute(text(validated_sql.sql))
                return [PropertyRow.from_mapping(dict(r._mapping)) for r in result]
        except OperationalError as exc:
            raise DatabaseError(str(exc.orig) if exc.orig else str(exc)) from exc
        except SQLAlchemyError as exc:
            raise DatabaseError(str(exc)) from exc

    async def healthcheck(self) -> bool:
        return await self._datasource.healthcheck()


class InMemoryPropertyRepository(PropertyRepository):
    """Para tests sin DB."""

    def __init__(self, rows: Sequence[PropertyRow]) -> None:
        self._rows = list(rows)

    async def execute_validated_select(
        self,
        validated_sql: ValidatedSQL,  # noqa: ARG002 — requerido por ABC; mock ignora el SQL
    ) -> Sequence[PropertyRow]:
        return list(self._rows)

    async def healthcheck(self) -> bool:
        return True


def build_property_repository(datasource: DataSource, settings: Settings) -> PropertyRepository:
    if settings.DB_BACKEND == "mysql":
        return MySQLPropertyRepository(datasource)
    raise ValueError(f"Unknown DB_BACKEND={settings.DB_BACKEND}")
