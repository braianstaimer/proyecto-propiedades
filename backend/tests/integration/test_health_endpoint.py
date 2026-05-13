from __future__ import annotations


def test_health_returns_ok_when_all_up(integration_client) -> None:
    response = integration_client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["db"] == "ok"
    assert body["llm"] == "ok"
    assert body["status"] in ("ok", "degraded")
    assert body["version"]


def test_openapi_schema_available(integration_client) -> None:
    response = integration_client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert spec["info"]["title"] == "proyecto-propiedades API"
    assert "/api/search" in spec["paths"]
    assert "/api/health" in spec["paths"]
