"""Smoke tests · golden path para release.

Estos tests validan que el stack arranca y los caminos críticos retornan 200
con shapes correctos. Se corren con marker `pytest -m smoke` para mantener
el ciclo de feedback de release rápido (no incluyen edge cases ni
parametrizaciones que viven en unit/integration).

Pre-requisitos:
- MySQL en localhost:3306 con seed (compose up del stack)
- LLM en MOCK_LLM=true (no requiere Ollama vivo)

Cobertura objetivo del smoke:
1. /api/health responde 200 con shape {status, db, llm, version}
2. Las 6 búsquedas del PDF retornan 200 con count>=1
3. El envelope de error es consistente para EMPTY_QUERY
4. La respuesta lleva X-Request-ID en headers
5. /openapi.json sigue exponiendo los 2 endpoints documentados
"""
from __future__ import annotations

import pytest

PDF_QUERIES = (
    "Busco casas de 3 habitaciones en zona 10",
    "Muéstrame departamentos de menos de $150,000",
    "Propiedades con más de 2 baños y al menos 150 metros cuadrados",
    "Casas publicadas en los últimos 30 días",
    "Terrenos en venta con precio entre $50,000 y $100,000",
    "Departamentos con 2 habitaciones en zona 15",
)


@pytest.mark.smoke
def test_health_endpoint_shape(integration_client) -> None:
    """Health responde 200 con el shape documentado en OpenAPI."""
    response = integration_client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"status", "db", "llm", "version"}
    assert body["status"] in {"ok", "degraded"}
    assert body["db"] in {"ok", "down"}
    assert body["llm"] in {"ok", "down"}
    assert isinstance(body["version"], str)


@pytest.mark.smoke
@pytest.mark.parametrize("query", PDF_QUERIES, ids=lambda q: q[:40].replace(" ", "_"))
def test_pdf_query_golden_path(integration_client, query: str) -> None:
    """Las 6 búsquedas del PDF retornan 200 con count >= 1."""
    response = integration_client.post("/api/search", json={"query": query})

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["query"] == query
    assert body["sql"].lower().startswith("select")
    assert "propiedades" in body["sql"].lower()
    assert body["count"] >= 1
    assert isinstance(body["results"], list)
    assert len(body["results"]) == body["count"]
    assert isinstance(body["took_ms"], int) and body["took_ms"] >= 0


@pytest.mark.smoke
def test_result_property_shape(integration_client) -> None:
    """Una propiedad devuelta lleva todos los campos del PDF."""
    response = integration_client.post(
        "/api/search", json={"query": PDF_QUERIES[0]}
    )

    body = response.json()
    first = body["results"][0]
    expected_keys = {
        "id", "titulo", "descripcion", "tipo", "precio",
        "habitaciones", "banos", "area_m2", "ubicacion", "fecha_publicacion",
    }
    assert set(first.keys()) == expected_keys
    assert first["tipo"] in {"casa", "departamento", "terreno", "oficina", "local"}


@pytest.mark.smoke
def test_empty_query_returns_envelope(integration_client) -> None:
    """Query vacío → envelope con code=EMPTY_QUERY (no FastAPI raw 422)."""
    response = integration_client.post("/api/search", json={"query": ""})

    assert response.status_code == 422
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "EMPTY_QUERY"
    assert isinstance(body["error"]["message"], str)


@pytest.mark.smoke
def test_request_id_propagated(integration_client) -> None:
    """X-Request-ID lleva el valor del cliente o uno generado."""
    custom_id = "smoke-request-id-001"
    response = integration_client.post(
        "/api/search",
        json={"query": PDF_QUERIES[0]},
        headers={"X-Request-ID": custom_id},
    )

    assert response.headers["x-request-id"] == custom_id


@pytest.mark.smoke
def test_request_id_generated_when_absent(integration_client) -> None:
    """Sin X-Request-ID en el request, el server genera uno (UUID-like)."""
    response = integration_client.post(
        "/api/search", json={"query": PDF_QUERIES[0]}
    )

    request_id = response.headers.get("x-request-id")
    assert request_id is not None
    assert len(request_id) >= 8


@pytest.mark.smoke
def test_openapi_exposes_documented_paths(integration_client) -> None:
    """OpenAPI sigue exponiendo los 2 endpoints públicos."""
    response = integration_client.get("/openapi.json")

    assert response.status_code == 200
    spec = response.json()
    assert spec["info"]["title"] == "proyecto-propiedades API"
    assert "/api/search" in spec["paths"]
    assert "/api/health" in spec["paths"]
    assert spec["paths"]["/api/search"]["post"]["operationId"] == "searchProperties"
    assert spec["paths"]["/api/health"]["get"]["operationId"] == "getHealth"


@pytest.mark.smoke
def test_swagger_ui_served(integration_client) -> None:
    """`/docs` responde 200 con HTML."""
    response = integration_client.get("/docs")

    assert response.status_code == 200
    assert "swagger" in response.text.lower()
