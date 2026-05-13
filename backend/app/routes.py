from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app import __version__
from app.dependencies import (
    get_llm_provider,
    get_property_repository,
    get_search_service,
)
from app.llm_service import LLMProvider
from app.repositories import PropertyRepository
from app.schemas import (
    ErrorResponse,
    HealthResponse,
    SearchRequest,
    SearchResponse,
)
from app.search_service import SearchService

SearchServiceDep = Annotated[SearchService, Depends(get_search_service)]
PropertyRepositoryDep = Annotated[PropertyRepository, Depends(get_property_repository)]
LLMProviderDep = Annotated[LLMProvider, Depends(get_llm_provider)]

router = APIRouter(prefix="/api", tags=["search"])


@router.post(
    "/search",
    response_model=SearchResponse,
    operation_id="searchProperties",
    responses={
        400: {"model": ErrorResponse, "description": "Query vacía, larga o con caracteres no permitidos."},
        422: {"model": ErrorResponse, "description": "El LLM falló o el SQL generado no pasó validación."},
        429: {"model": ErrorResponse, "description": "Rate limit excedido (si habilitado)."},
        500: {"model": ErrorResponse, "description": "Error en MySQL."},
        503: {"model": ErrorResponse, "description": "LLM (Ollama) no disponible."},
    },
    summary="Buscar propiedades en lenguaje natural",
    description=(
        "Recibe una consulta en español natural y devuelve propiedades coincidentes. "
        "Internamente: sanitiza el input, lo envía al LLM local para generar SQL, "
        "valida con sqlglot AST + whitelist (sólo SELECT sobre `propiedades`), y "
        "ejecuta el SQL validado contra MySQL."
    ),
)
async def search(payload: SearchRequest, service: SearchServiceDep) -> SearchResponse:
    return await service.search(payload.query)


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    operation_id="getHealth",
    summary="Estado del backend, DB y LLM",
    description=(
        "Devuelve `ok` si DB y LLM responden. Devuelve `degraded` si alguno está caído. "
        "Útil para sondas de liveness/readiness y para diagnóstico desde el frontend."
    ),
)
async def health(repo: PropertyRepositoryDep, llm: LLMProviderDep) -> HealthResponse:
    db_ok = await repo.healthcheck()
    llm_ok = await llm.healthcheck()
    status = "ok" if (db_ok and llm_ok) else "degraded"
    return HealthResponse(
        status=status,  # type: ignore[arg-type]
        db="ok" if db_ok else "down",
        llm="ok" if llm_ok else "down",
        version=__version__,
    )
