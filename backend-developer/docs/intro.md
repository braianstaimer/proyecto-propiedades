---
sidebar_position: 1
title: Quickstart
slug: /intro
---

# proyecto-propiedades · API Documentation

API REST en **FastAPI 0.115 + MySQL 8 + Ollama** que traduce consultas en lenguaje natural a SQL y devuelve propiedades inmobiliarias coincidentes.

> **Stack:** FastAPI · Pydantic v2 · SQLAlchemy 2 async · aiomysql · sqlglot · Ollama `llama3.2:3b`.

## Levantar el stack en local

Pre-requisito: Docker, y Ollama corriendo en el host con `llama3.2:3b` pulled.

```bash
cd proyecto-propiedades
cp .env.example .env
docker compose up -d --build
```

Verifique los 3 servicios:

```bash
curl http://localhost:8000/api/health
# { "status":"ok", "db":"ok", "llm":"ok", "version":"0.1.0" }

open http://localhost:8080   # frontend Vue
```

## Probar el endpoint principal

```bash
curl -X POST http://localhost:8000/api/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"Busco casas de 3 habitaciones en zona 10"}'
```

Respuesta:

```json
{
  "query": "Busco casas de 3 habitaciones en zona 10",
  "sql": "SELECT id, titulo, descripcion, tipo, precio, habitaciones, banos, area_m2, ubicacion, fecha_publicacion FROM propiedades WHERE tipo = 'casa' AND habitaciones = 3 AND LOWER(ubicacion) LIKE '%zona 10%' LIMIT 50",
  "count": 2,
  "results": [
    {
      "id": 1,
      "titulo": "Casa moderna en Zona 10",
      "tipo": "casa",
      "precio": 320000.00,
      "habitaciones": 3,
      "banos": 3,
      "area_m2": 240.0,
      "ubicacion": "Zona 10, Guatemala",
      "fecha_publicacion": "2026-04-21"
    }
  ],
  "took_ms": 1820
}
```

## Por dónde seguir

| Sección | Contenido |
|---|---|
| [Flujo de búsqueda](/flows/search-flow) | Sequence diagram NL → SQL → resultados |
| [Catálogo de errores](/architecture/error-codes) | Códigos de error con HTTP status y causa |
| [Referencia de Health](/reference/health) | Endpoint de salud y semántica |
| [API Reference](/api-reference) | Spec OpenAPI interactiva (Scalar) |
