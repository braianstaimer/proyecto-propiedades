from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TipoPropiedad = Literal["casa", "departamento", "terreno", "oficina", "local"]


class SearchRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"query": "Busco casas de 3 habitaciones en zona 10"}
        }
    )

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Consulta en lenguaje natural (1–500 caracteres).",
        examples=["Busco casas de 3 habitaciones en zona 10"],
    )


class PropertyOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "titulo": "Casa moderna en Zona 10",
                "descripcion": "Acabados de lujo, jardín y parqueo doble.",
                "tipo": "casa",
                "precio": 320000.00,
                "habitaciones": 3,
                "banos": 3,
                "area_m2": 240.0,
                "ubicacion": "Zona 10, Guatemala",
                "fecha_publicacion": "2026-04-21",
            }
        },
    )

    id: int = Field(..., description="Identificador único de la propiedad.")
    titulo: str = Field(..., description="Título descriptivo (máx 180 chars).")
    descripcion: str | None = Field(None, description="Descripción larga opcional.")
    tipo: TipoPropiedad = Field(..., description="Categoría de propiedad.")
    precio: float = Field(..., ge=0, description="Precio en USD.")
    habitaciones: int | None = Field(None, ge=0, description="# de habitaciones.")
    banos: int | None = Field(None, ge=0, description="# de baños.")
    area_m2: float | None = Field(None, ge=0, description="Área en m².")
    ubicacion: str = Field(..., description="Zona/ubicación (texto libre).")
    fecha_publicacion: date = Field(..., description="Fecha en que se publicó la propiedad.")


class SearchResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "Busco casas de 3 habitaciones en zona 10",
                "sql": (
                    "SELECT id, titulo, descripcion, tipo, precio, habitaciones, banos, "
                    "area_m2, ubicacion, fecha_publicacion FROM propiedades "
                    "WHERE tipo = 'casa' AND habitaciones = 3 "
                    "AND LOWER(ubicacion) LIKE '%zona 10%' LIMIT 50"
                ),
                "count": 2,
                "results": [
                    {
                        "id": 1,
                        "titulo": "Casa moderna en Zona 10",
                        "descripcion": "Acabados de lujo.",
                        "tipo": "casa",
                        "precio": 320000.0,
                        "habitaciones": 3,
                        "banos": 3,
                        "area_m2": 240.0,
                        "ubicacion": "Zona 10, Guatemala",
                        "fecha_publicacion": "2026-04-21",
                    }
                ],
                "took_ms": 1820,
            }
        }
    )

    query: str = Field(..., description="Consulta NL recibida (saneada).")
    sql: str = Field(..., description="SQL ejecutado tras validación.")
    count: int = Field(..., ge=0, description="Número de resultados retornados.")
    results: list[PropertyOut] = Field(..., description="Lista de propiedades coincidentes.")
    took_ms: int = Field(..., ge=0, description="Tiempo de procesamiento en ms.")


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Código de error del catálogo (SCREAMING_SNAKE_CASE).")
    message: str = Field(..., description="Mensaje humano en español.")
    detail: str | None = Field(None, description="Detalle técnico opcional.")
    request_id: str | None = Field(None, description="ID de correlación de la request.")


class ErrorResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "LLM_TIMEOUT",
                    "message": "El modelo tardó más del tiempo permitido. Intente de nuevo.",
                    "detail": None,
                    "request_id": "01H8X...",
                }
            }
        }
    )
    error: ErrorDetail


class HealthResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"status": "ok", "db": "ok", "llm": "ok", "version": "0.1.0"}
        }
    )
    status: Literal["ok", "degraded"] = Field("ok", description="Estado global.")
    db: Literal["ok", "down"] = Field(..., description="Estado MySQL.")
    llm: Literal["ok", "down"] = Field(..., description="Estado LLM.")
    version: str = Field(..., description="Versión del backend.")
