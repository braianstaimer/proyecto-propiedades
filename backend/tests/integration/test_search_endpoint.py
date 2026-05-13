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


@pytest.mark.parametrize("query", PDF_QUERIES)
def test_pdf_query_returns_results(integration_client, query: str) -> None:
    response = integration_client.post("/api/search", json={"query": query})
    assert response.status_code == 200
    body = response.json()
    assert body["query"] == query
    assert body["sql"].lower().startswith("select")
    assert body["count"] >= 1
    assert isinstance(body["results"], list)
    assert body["took_ms"] >= 0


def test_search_returns_request_id_header(integration_client) -> None:
    response = integration_client.post(
        "/api/search", json={"query": PDF_QUERIES[0]}, headers={"X-Request-ID": "demo-001"}
    )
    assert response.headers["x-request-id"] == "demo-001"


def test_search_generates_request_id_when_missing(integration_client) -> None:
    response = integration_client.post("/api/search", json={"query": PDF_QUERIES[0]})
    assert response.headers.get("x-request-id")


def test_search_empty_query_returns_422(integration_client) -> None:
    response = integration_client.post("/api/search", json={"query": ""})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "EMPTY_QUERY"


def test_search_long_query_returns_422(integration_client) -> None:
    response = integration_client.post("/api/search", json={"query": "a" * 501})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "EMPTY_QUERY"


def test_search_missing_query_returns_422(integration_client) -> None:
    response = integration_client.post("/api/search", json={})
    assert response.status_code == 422
    assert response.json()["error"]["code"] in ("EMPTY_QUERY", "VALIDATION_ERROR")
