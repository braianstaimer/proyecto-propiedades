from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import cast

import pytest

from app.config import Settings
from app.exceptions import (
    DomainError,
    EmptyQueryError,
)
from app.llm_service import LLMProvider
from app.prompts import COLUMN_LIST
from app.repositories import InMemoryPropertyRepository, PropertyRepository, PropertyRow
from app.search_service import SearchService
from app.sql_validator import SQLValidator, ValidatedSQL

SAMPLE_ROW = PropertyRow(
    id=1,
    titulo="x",
    descripcion=None,
    tipo="casa",
    precio=1.0,
    habitaciones=1,
    banos=1,
    area_m2=1.0,
    ubicacion="Zona 1, Guatemala",
    fecha_publicacion=date(2026, 1, 1),
)


class FakeLLM:
    def __init__(self, *responses: str) -> None:
        self._responses = list(responses)
        self._calls: list[str] = []

    async def generate_sql(self, nl_query: str, *, timeout_seconds: int) -> str:
        self._calls.append(nl_query)
        if not self._responses:
            raise RuntimeError("FakeLLM out of responses")
        return self._responses.pop(0)

    async def healthcheck(self) -> bool:
        return True

    async def close(self) -> None: ...

    @property
    def calls(self) -> list[str]:
        return self._calls


def _settings(**overrides) -> Settings:
    base = {
        "DB_BACKEND": "mysql",
        "LLM_BACKEND": "mock",
        "OLLAMA_TIMEOUT_SECONDS": 5,
        "MAX_QUERY_LENGTH": 500,
        **overrides,
    }
    return Settings(**base)


def _service(llm: LLMProvider, repo: PropertyRepository | None = None) -> SearchService:
    return SearchService(
        llm=llm,
        validator=SQLValidator(allowed_tables={"propiedades"}),
        repo=repo or InMemoryPropertyRepository([SAMPLE_ROW]),
        settings=_settings(),
    )


@pytest.mark.asyncio
async def test_happy_path_returns_response() -> None:
    llm = FakeLLM(f"SELECT {COLUMN_LIST} FROM propiedades LIMIT 5")
    service = _service(cast(LLMProvider, llm))
    response = await service.search("cualquier consulta")
    assert response.count == 1
    assert response.took_ms >= 0
    assert response.sql.lower().startswith("select")


@pytest.mark.asyncio
async def test_empty_query_rejected() -> None:
    service = _service(cast(LLMProvider, FakeLLM("SELECT 1 FROM propiedades")))
    with pytest.raises(EmptyQueryError):
        await service.search("   ")


@pytest.mark.asyncio
async def test_query_too_long_rejected() -> None:
    service = _service(cast(LLMProvider, FakeLLM("SELECT 1 FROM propiedades")))
    with pytest.raises(EmptyQueryError):
        await service.search("a" * 501)


@pytest.mark.asyncio
async def test_control_chars_rejected() -> None:
    service = _service(cast(LLMProvider, FakeLLM("SELECT 1 FROM propiedades")))
    with pytest.raises(EmptyQueryError):
        await service.search("hello\x00world")


@pytest.mark.asyncio
async def test_retry_on_invalid_sql_succeeds() -> None:
    llm = FakeLLM("DROP TABLE propiedades", f"SELECT {COLUMN_LIST} FROM propiedades LIMIT 1")
    service = _service(cast(LLMProvider, llm))
    response = await service.search("test")
    assert response.count == 1
    assert len(llm.calls) == 2


@pytest.mark.asyncio
async def test_retry_failure_raises_first_error() -> None:
    llm = FakeLLM("DROP TABLE propiedades", "ALSO INVALID")
    service = _service(cast(LLMProvider, llm))
    with pytest.raises(DomainError) as excinfo:
        await service.search("test")
    assert excinfo.value.code in ("SQL_NOT_SELECT", "LLM_INVALID_OUTPUT")


@pytest.mark.asyncio
async def test_sanitize_strips_whitespace() -> None:
    llm = FakeLLM(f"SELECT {COLUMN_LIST} FROM propiedades LIMIT 1")
    service = _service(cast(LLMProvider, llm))
    response = await service.search("  Busco casas  ")
    assert response.query == "Busco casas"


@pytest.mark.asyncio
async def test_service_depends_only_on_abstractions() -> None:
    """Sanity check: el constructor solo acepta abstracciones."""
    import inspect

    sig = inspect.signature(SearchService.__init__)
    annotations = {name: p.annotation for name, p in sig.parameters.items() if name != "self"}
    # llm: LLMProvider, repo: PropertyRepository — abstracciones
    assert "LLMProvider" in str(annotations.get("llm", ""))
    assert "PropertyRepository" in str(annotations.get("repo", ""))


@pytest.mark.asyncio
async def test_response_results_are_pydantic() -> None:
    from app.schemas import PropertyOut

    llm = FakeLLM(f"SELECT {COLUMN_LIST} FROM propiedades LIMIT 1")
    service = _service(cast(LLMProvider, llm))
    response = await service.search("test")
    assert all(isinstance(r, PropertyOut) for r in response.results)


@pytest.mark.asyncio
async def test_validated_sql_passed_to_repo() -> None:
    captured: list[ValidatedSQL] = []

    class CapturingRepo(PropertyRepository):
        async def execute_validated_select(self, validated_sql: ValidatedSQL) -> Sequence[PropertyRow]:
            captured.append(validated_sql)
            return [SAMPLE_ROW]

        async def healthcheck(self) -> bool:
            return True

    llm = FakeLLM(f"SELECT {COLUMN_LIST} FROM propiedades LIMIT 1")
    service = _service(cast(LLMProvider, llm), CapturingRepo())
    await service.search("test")
    assert len(captured) == 1
    assert isinstance(captured[0], ValidatedSQL)


@pytest.mark.asyncio
async def test_forbidden_table_propagates_after_retry() -> None:
    llm = FakeLLM("SELECT * FROM users", "SELECT * FROM users")
    service = _service(cast(LLMProvider, llm))
    with pytest.raises(DomainError):
        await service.search("hack")


@pytest.mark.asyncio
async def test_invalid_output_then_recover() -> None:
    llm = FakeLLM("", f"SELECT {COLUMN_LIST} FROM propiedades LIMIT 1")
    service = _service(cast(LLMProvider, llm))
    response = await service.search("test")
    assert response.count == 1
