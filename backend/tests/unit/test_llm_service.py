from __future__ import annotations

import httpx
import pytest

from app.exceptions import LLMInvalidOutputError, LLMTimeoutError, LLMUnavailableError
from app.llm_service import MockLLMProvider, OllamaLLMProvider
from app.prompts import PromptBuilder


def _ollama_mock_response(text: str) -> dict:
    return {"response": text, "done": True}


def _make_provider(handler: httpx.MockTransport) -> OllamaLLMProvider:
    client = httpx.AsyncClient(transport=handler)
    return OllamaLLMProvider(
        base_url="http://localhost:11434",
        model="llama3.2:3b",
        prompt_builder=PromptBuilder(),
        client=client,
    )


@pytest.mark.asyncio
async def test_strip_markdown_block() -> None:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=_ollama_mock_response("```sql\nSELECT 1\n```"))
    )
    provider = _make_provider(transport)
    result = await provider.generate_sql("any", timeout_seconds=5)
    assert result == "SELECT 1"


@pytest.mark.asyncio
async def test_timeout_raises_typed() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("simulated", request=req)

    transport = httpx.MockTransport(handler)
    provider = _make_provider(transport)
    with pytest.raises(LLMTimeoutError):
        await provider.generate_sql("any", timeout_seconds=1)


@pytest.mark.asyncio
async def test_connect_error_raises_typed() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=req)

    transport = httpx.MockTransport(handler)
    provider = _make_provider(transport)
    with pytest.raises(LLMUnavailableError):
        await provider.generate_sql("any", timeout_seconds=5)


@pytest.mark.asyncio
async def test_server_error_raises_unavailable() -> None:
    transport = httpx.MockTransport(lambda req: httpx.Response(503, text="busy"))
    provider = _make_provider(transport)
    with pytest.raises(LLMUnavailableError):
        await provider.generate_sql("any", timeout_seconds=5)


@pytest.mark.asyncio
async def test_invalid_json_raises_typed() -> None:
    transport = httpx.MockTransport(lambda req: httpx.Response(200, text="not json"))
    provider = _make_provider(transport)
    with pytest.raises(LLMInvalidOutputError):
        await provider.generate_sql("any", timeout_seconds=5)


@pytest.mark.asyncio
async def test_healthcheck_ok() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        if "/api/tags" in str(req.url):
            return httpx.Response(200, json={"models": []})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    provider = _make_provider(transport)
    assert await provider.healthcheck() is True


@pytest.mark.asyncio
async def test_healthcheck_false_on_error() -> None:
    transport = httpx.MockTransport(
        lambda req: (_ for _ in ()).throw(httpx.ConnectError("x", request=req))
    )
    provider = _make_provider(transport)
    assert await provider.healthcheck() is False


@pytest.mark.asyncio
async def test_mock_provider_matches_canned() -> None:
    provider = MockLLMProvider()
    sql = await provider.generate_sql(
        "Busco casas de 3 habitaciones en zona 10", timeout_seconds=5
    )
    assert "habitaciones = 3" in sql
    assert "casa" in sql
    assert "zona 10" in sql


@pytest.mark.asyncio
async def test_mock_provider_falls_back_to_default() -> None:
    provider = MockLLMProvider()
    sql = await provider.generate_sql("algo no mapeado", timeout_seconds=5)
    assert "propiedades" in sql.lower()


@pytest.mark.asyncio
async def test_mock_provider_with_fixed_response() -> None:
    provider = MockLLMProvider(fixed_response="SELECT 1 FROM propiedades LIMIT 1")
    sql = await provider.generate_sql("ignored", timeout_seconds=5)
    assert sql == "SELECT 1 FROM propiedades LIMIT 1"
