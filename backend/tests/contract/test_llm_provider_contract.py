"""Cross-implementation contract tests for LLMProvider (LSP)."""
from __future__ import annotations

import httpx
import pytest

from app.llm_service import LLMProvider, MockLLMProvider, OllamaLLMProvider
from app.prompts import PromptBuilder


def _ollama_with_mock_http() -> OllamaLLMProvider:
    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json={"response": "SELECT 1 FROM propiedades LIMIT 1", "done": True})
    )
    client = httpx.AsyncClient(transport=transport)
    return OllamaLLMProvider(
        base_url="http://stub",
        model="llama3.2:3b",
        prompt_builder=PromptBuilder(),
        client=client,
    )


PROVIDERS_FACTORIES = [
    pytest.param(lambda: MockLLMProvider(fixed_response="SELECT id FROM propiedades LIMIT 1"), id="mock"),
    pytest.param(_ollama_with_mock_http, id="ollama-mock-http"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("factory", PROVIDERS_FACTORIES)
async def test_generate_sql_returns_str(factory) -> None:
    provider: LLMProvider = factory()
    result = await provider.generate_sql("Busco casas", timeout_seconds=5)
    assert isinstance(result, str)
    assert result.strip()


@pytest.mark.asyncio
@pytest.mark.parametrize("factory", PROVIDERS_FACTORIES)
async def test_healthcheck_returns_bool(factory) -> None:
    provider: LLMProvider = factory()
    result = await provider.healthcheck()
    assert isinstance(result, bool)


@pytest.mark.asyncio
@pytest.mark.parametrize("factory", PROVIDERS_FACTORIES)
async def test_close_is_callable(factory) -> None:
    provider: LLMProvider = factory()
    await provider.close()
