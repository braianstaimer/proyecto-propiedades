from __future__ import annotations

import json
from pathlib import Path

SNAPSHOT_PATH = Path(__file__).parent / "openapi_snapshot.json"


def _normalize(spec: dict) -> dict:
    return {
        "openapi": spec.get("openapi"),
        "info": {
            "title": spec["info"]["title"],
            "version": spec["info"]["version"],
        },
        "paths": sorted(spec["paths"].keys()),
        "operations": sorted(
            f"{method.upper()} {path}"
            for path, ops in spec["paths"].items()
            for method in ops
        ),
        "components_schemas": sorted(spec.get("components", {}).get("schemas", {}).keys()),
    }


def test_openapi_snapshot_stable(integration_client) -> None:
    actual = _normalize(integration_client.get("/openapi.json").json())
    if not SNAPSHOT_PATH.exists():
        SNAPSHOT_PATH.write_text(json.dumps(actual, indent=2, sort_keys=True))
        return
    expected = json.loads(SNAPSHOT_PATH.read_text())
    assert actual == expected, (
        "OpenAPI surface changed. If intentional, delete "
        f"{SNAPSHOT_PATH.name} y vuelva a correr el test para regenerarlo."
    )
