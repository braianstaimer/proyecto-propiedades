from __future__ import annotations

import re
import time
import unicodedata

from app.config import Settings
from app.exceptions import (
    DomainError,
    EmptyQueryError,
    LLMInvalidOutputError,
)
from app.llm_service import LLMProvider
from app.repositories import PropertyRepository, PropertyRow
from app.schemas import PropertyOut, SearchResponse
from app.sql_validator import SQLValidator

CONTROL_CHARS_PATTERN = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f"

# Marcadores típicos de prompt-injection. El match es case-insensitive y se
# evalúa sobre la versión normalizada (NFKC + lowercase) para neutralizar
# homoglyphs Unicode y mayúsculas mezcladas.
_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    # Delimitadores de bloque que intentan "cerrar" el contexto del prompt.
    re.compile(r"```"),
    re.compile(r'"""'),
    re.compile(r"<\|.*?\|>"),
    re.compile(r"</?\s*(system|user|assistant|instruction|s)\s*>", re.IGNORECASE),
    # Roles / tags clásicos del template (rompen la conversación).
    re.compile(r"\b(system|assistant|usuario|user)\s*:\s*", re.IGNORECASE),
    re.compile(r"\bsql\s*:\s*", re.IGNORECASE),
    # Comandos override.
    re.compile(
        r"\b(ignore|disregard|forget|override|olvida|ignora|descarta)\b.{0,40}\b"
        r"(previous|above|prior|anterior|todas|reglas|instructions|instrucciones|"
        r"system|prompt)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(you\s+are\s+now|act\s+as|actua\s+como|act[uú]a\s+como|eres\s+ahora|"
        r"pretend(\s+to\s+be)?|new\s+(instructions|rules)|nuevas\s+instrucciones)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(jailbreak|developer\s+mode|DAN)\b", re.IGNORECASE),
)


class SearchService:
    """Orquesta NL → SQL → resultados. Agnóstico de provider concreto."""

    def __init__(
        self,
        *,
        llm: LLMProvider,
        validator: SQLValidator,
        repo: PropertyRepository,
        settings: Settings,
    ) -> None:
        self._llm = llm
        self._validator = validator
        self._repo = repo
        self._max_query_length = settings.MAX_QUERY_LENGTH
        self._llm_timeout = settings.OLLAMA_TIMEOUT_SECONDS

    async def search(self, query: str) -> SearchResponse:
        start = time.perf_counter()
        sanitized = self._sanitize(query)
        validated = await self._generate_and_validate(sanitized)
        rows = await self._repo.execute_validated_select(validated)
        took_ms = int((time.perf_counter() - start) * 1000)
        return SearchResponse(
            query=sanitized,
            sql=validated.sql,
            count=len(rows),
            results=[self._to_property_out(r) for r in rows],
            took_ms=took_ms,
        )

    def _sanitize(self, query: str) -> str:
        if query is None:
            raise EmptyQueryError("query=None")
        # NFKC neutraliza homoglyphs (cirílica/latina) y formas compatibles
        # antes de cualquier chequeo de longitud o patrones.
        normalized = unicodedata.normalize("NFKC", query)
        trimmed = normalized.strip()
        if not trimmed:
            raise EmptyQueryError("query vacía")
        if len(trimmed) > self._max_query_length:
            raise EmptyQueryError(f"query > {self._max_query_length} chars")
        if any(c in CONTROL_CHARS_PATTERN for c in trimmed):
            raise EmptyQueryError("query contiene caracteres de control")
        # CR/LF dentro del input son ruido natural pero un canal clásico para
        # "cerrar" el contexto del prompt e inyectar pseudo-turnos nuevos.
        if "\n" in trimmed or "\r" in trimmed:
            raise EmptyQueryError("query no puede contener saltos de línea")
        # Bloquea marcadores típicos de prompt-injection (case-insensitive,
        # post-NFKC). Mensaje genérico para no enseñar la lista al atacante.
        lowered = trimmed.lower()
        for pattern in _INJECTION_PATTERNS:
            if pattern.search(lowered):
                raise EmptyQueryError("query contiene contenido no permitido")
        return trimmed

    async def _generate_and_validate(self, sanitized_query: str):
        raw_sql = await self._llm.generate_sql(sanitized_query, timeout_seconds=self._llm_timeout)
        try:
            return self._validator.validate(raw_sql)
        except DomainError as initial_error:
            return await self._retry_once(sanitized_query, initial_error)

    async def _retry_once(self, sanitized_query: str, initial_error: DomainError):
        # IMPORTANTE: NO concatenamos `initial_error.code` al sanitized_query
        # antes de enviarlo al LLM. Esa concatenación reabriría el canal de
        # prompt-injection: el user_query del atacante volvería a viajar como
        # NL y, al combinarse con texto adicional, podría escapar el contexto
        # del template. El retry usa el MISMO sanitized_query original; la
        # corrección viene del propio LLM tras re-ver el system prompt.
        retry_raw = await self._llm.generate_sql(
            sanitized_query,
            timeout_seconds=self._llm_timeout,
        )
        try:
            return self._validator.validate(retry_raw)
        except DomainError:
            raise initial_error from None

    @staticmethod
    def _to_property_out(row: PropertyRow) -> PropertyOut:
        return PropertyOut(
            id=row.id,
            titulo=row.titulo,
            descripcion=row.descripcion,
            tipo=row.tipo,  # type: ignore[arg-type]
            precio=row.precio,
            habitaciones=row.habitaciones,
            banos=row.banos,
            area_m2=row.area_m2,
            ubicacion=row.ubicacion,
            fecha_publicacion=row.fecha_publicacion,
        )


__all__ = ["SearchService", "LLMInvalidOutputError"]
