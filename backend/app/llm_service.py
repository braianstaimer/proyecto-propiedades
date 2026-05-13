from __future__ import annotations

import logging
import re
from typing import Protocol, runtime_checkable

import httpx

from app.config import Settings
from app.exceptions import LLMInvalidOutputError, LLMTimeoutError, LLMUnavailableError
from app.prompts import COLUMN_LIST, PromptBuilder

logger = logging.getLogger(__name__)


@runtime_checkable
class LLMProvider(Protocol):
    async def generate_sql(self, nl_query: str, *, timeout_seconds: int) -> str: ...
    async def healthcheck(self) -> bool: ...
    async def close(self) -> None: ...


class OllamaLLMProvider:
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        prompt_builder: PromptBuilder,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._prompt_builder = prompt_builder
        self._client = client or httpx.AsyncClient()
        self._owns_client = client is None

    async def generate_sql(self, nl_query: str, *, timeout_seconds: int) -> str:
        prompt = self._prompt_builder.build(nl_query)
        try:
            response = await self._client.post(
                f"{self._base_url}/api/generate",
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.0},
                },
                timeout=timeout_seconds,
            )
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError(f"timeout={timeout_seconds}s") from exc
        except httpx.ConnectError as exc:
            raise LLMUnavailableError(self._base_url) from exc
        if response.status_code >= 500:
            raise LLMUnavailableError(f"Ollama HTTP {response.status_code}")
        try:
            body = response.json()
        except ValueError as exc:
            raise LLMInvalidOutputError("Respuesta no es JSON.") from exc
        raw = body.get("response", "")
        return self._post_process(raw)

    async def healthcheck(self) -> bool:
        try:
            r = await self._client.get(f"{self._base_url}/api/tags", timeout=5)
            return r.status_code == 200
        except (httpx.HTTPError, OSError) as exc:
            logger.warning("llm.healthcheck.failed", exc_info=exc)
            return False

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    @staticmethod
    def _post_process(raw: str) -> str:
        s = raw.strip()
        s = re.sub(r"^```(?:sql|SQL)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
        return s.strip()


_CANNED_SQL_BY_KEYWORD: tuple[tuple[tuple[str, ...], str], ...] = (
    (("casa", "zona 10", "3"), f"SELECT {COLUMN_LIST} FROM propiedades WHERE tipo = 'casa' AND habitaciones = 3 AND LOWER(ubicacion) LIKE '%zona 10%' LIMIT 50"),
    (("departamento", "150"), f"SELECT {COLUMN_LIST} FROM propiedades WHERE tipo = 'departamento' AND precio < 150000 LIMIT 50"),
    (("baño", "150"), f"SELECT {COLUMN_LIST} FROM propiedades WHERE banos > 2 AND area_m2 >= 150 LIMIT 50"),
    (("bano", "150"), f"SELECT {COLUMN_LIST} FROM propiedades WHERE banos > 2 AND area_m2 >= 150 LIMIT 50"),
    (("casa", "30", "día"), f"SELECT {COLUMN_LIST} FROM propiedades WHERE tipo = 'casa' AND fecha_publicacion >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) LIMIT 50"),
    (("casa", "30", "dia"), f"SELECT {COLUMN_LIST} FROM propiedades WHERE tipo = 'casa' AND fecha_publicacion >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) LIMIT 50"),
    (("terreno", "50", "100"), f"SELECT {COLUMN_LIST} FROM propiedades WHERE tipo = 'terreno' AND precio BETWEEN 50000 AND 100000 LIMIT 50"),
    (("departamento", "zona 15"), f"SELECT {COLUMN_LIST} FROM propiedades WHERE tipo = 'departamento' AND habitaciones = 2 AND LOWER(ubicacion) LIKE '%zona 15%' LIMIT 50"),
)
DEFAULT_CANNED: str = f"SELECT {COLUMN_LIST} FROM propiedades LIMIT 10"


class MockLLMProvider:
    """Devuelve SQL canned mapeado a las 6 búsquedas del PDF. Para tests + emergency demo."""

    def __init__(self, fixed_response: str | None = None) -> None:
        self._fixed_response = fixed_response

    async def generate_sql(self, nl_query: str, *, timeout_seconds: int) -> str:  # noqa: ARG002
        # timeout_seconds requerido por LLMProvider Protocol; el mock no hace I/O.
        if self._fixed_response is not None:
            return self._fixed_response
        return self._match(nl_query)

    async def healthcheck(self) -> bool:
        return True

    async def close(self) -> None:
        return None

    @staticmethod
    def _match(query: str) -> str:
        q = query.lower()
        for keywords, sql in _CANNED_SQL_BY_KEYWORD:
            if all(k in q for k in keywords):
                return sql
        return DEFAULT_CANNED


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.MOCK_LLM or settings.LLM_BACKEND == "mock":
        return MockLLMProvider()
    if settings.LLM_BACKEND == "ollama":
        return OllamaLLMProvider(
            base_url=settings.OLLAMA_URL,
            model=settings.OLLAMA_MODEL,
            prompt_builder=PromptBuilder(),
        )
    raise ValueError(f"Unknown LLM_BACKEND={settings.LLM_BACKEND}")
