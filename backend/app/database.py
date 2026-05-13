from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

if TYPE_CHECKING:
    from app.config import Settings


SessionContext = AbstractAsyncContextManager[AsyncSession]


class DataSource(ABC):
    @abstractmethod
    def session(self) -> SessionContext:
        raise NotImplementedError

    @abstractmethod
    async def healthcheck(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError


class MySQLDataSource(DataSource):
    def __init__(self, dsn: str, *, pool_size: int = 5, pool_recycle: int = 1800) -> None:
        self._engine = create_async_engine(
            dsn,
            pool_size=pool_size,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
            future=True,
        )
        self._session_factory = async_sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )

    def session(self) -> SessionContext:
        return self._open_session()

    @asynccontextmanager
    async def _open_session(self):
        async with self._session_factory() as s:
            yield s

    async def healthcheck(self) -> bool:
        try:
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def close(self) -> None:
        await self._engine.dispose()


def build_datasource(settings: Settings) -> DataSource:
    if settings.DB_BACKEND == "mysql":
        return MySQLDataSource(
            dsn=settings.mysql_dsn(),
            pool_size=settings.DB_POOL_SIZE,
            pool_recycle=settings.DB_POOL_RECYCLE_SECONDS,
        )
    raise ValueError(f"Unknown DB_BACKEND={settings.DB_BACKEND}")
