from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import HTMLResponse, JSONResponse

from app import __version__
from app.config import get_settings
from app.database import build_datasource
from app.exceptions import DomainError
from app.llm_service import build_llm_provider
from app.query_cache import QueryCache
from app.repositories import build_property_repository
from app.routes import router as api_router
from app.schemas import ErrorDetail, ErrorResponse
from app.search_service import SearchService
from app.sql_validator import SQLValidator
from persistencia.runner import run_migrations_if_needed

REDOC_JS_URL = "https://cdn.jsdelivr.net/npm/redoc@2.5.0/bundles/redoc.standalone.js"

logger = logging.getLogger("proyecto-propiedades")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    app.state.settings = settings
    app.state.datasource = build_datasource(settings)
    app.state.llm = build_llm_provider(settings)
    app.state.repo = build_property_repository(app.state.datasource, settings)
    app.state.validator = SQLValidator(
        allowed_tables={"propiedades"},
        max_limit=settings.MAX_SQL_LIMIT,
        default_limit=settings.DEFAULT_SQL_LIMIT,
    )
    app.state.query_cache = QueryCache(max_size=settings.QUERY_CACHE_SIZE)
    app.state.search_service = SearchService(
        llm=app.state.llm,
        validator=app.state.validator,
        repo=app.state.repo,
        settings=settings,
        cache=app.state.query_cache,
    )
    try:
        await run_migrations_if_needed(app.state.datasource, min_seed_rows=settings.MIN_SEED_ROWS)
    except Exception as exc:
        logger.warning("startup.migrations.failed", extra={"error": str(exc)})
    yield
    await app.state.datasource.close()
    await app.state.llm.close()


def _register_middleware(app: FastAPI, settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        body = ErrorResponse(
            error=ErrorDetail(
                code=exc.code,
                message=exc.message,
                detail=exc.detail,
                request_id=request_id,
            )
        )
        return JSONResponse(status_code=exc.http_status, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        code = _classify_validation_error(exc)
        body = ErrorResponse(
            error=ErrorDetail(
                code=code,
                message="La consulta no cumple el contrato esperado.",
                detail=str(exc.errors()[0]["msg"]) if exc.errors() else None,
                request_id=request_id,
            )
        )
        return JSONResponse(status_code=422, content=body.model_dump())


def _classify_validation_error(exc: RequestValidationError) -> str:
    for err in exc.errors():
        if err.get("loc", ())[-1:] == ("query",):
            return "EMPTY_QUERY"
    return "VALIDATION_ERROR"


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="proyecto-propiedades API",
        description=(
            "Búsqueda de propiedades inmobiliarias en lenguaje natural. "
            "Endpoint `POST /api/search` traduce NL a SQL vía LLM local (Ollama), "
            "valida con sqlglot AST y ejecuta sobre MySQL."
        ),
        version=__version__,
        contact={"name": "Braian Staimer", "url": "https://github.com/braianstaimer"},
        license_info={"name": "MIT"},
        lifespan=lifespan,
        redoc_url=None,  # se reemplaza por endpoint custom con CDN pineado (ver _register_redoc)
        openapi_tags=[
            {
                "name": "search",
                "description": "Búsqueda NL → SQL → resultados sobre la tabla `propiedades`.",
            },
            {
                "name": "health",
                "description": "Sondeo de estado del backend, MySQL y LLM.",
            },
        ],
    )
    _register_middleware(app, settings)
    _register_exception_handlers(app)
    _register_redoc(app)
    app.include_router(api_router)
    return app


def _register_redoc(app: FastAPI) -> None:
    """FastAPI 0.115 default usa `redoc@next` (CDN tag deprecada — render vacío).
    Servimos /redoc con un CDN pineado a 2.5.0 que sí soporta OpenAPI 3.1."""

    @app.get("/redoc", include_in_schema=False, response_class=HTMLResponse)
    async def custom_redoc() -> HTMLResponse:
        return get_redoc_html(
            openapi_url=app.openapi_url or "/openapi.json",
            title=f"{app.title} - ReDoc",
            redoc_js_url=REDOC_JS_URL,
        )


app = create_app()
