---
description: Audita la spec OpenAPI de backend endpoint por endpoint. Recortado del comando análogo de monorepo-de-referencia para alcance proyecto-propiedades (1 router, sin auth).
allowed-tools: Bash, Read, Edit, Write, Grep, Glob
---

# /audit-openapi · proyecto-propiedades

Audita la spec OpenAPI 3.1 generada por FastAPI en `backend/` y deja el spec listo para alimentar `backend-developer/`.

> **Alcance reducido vs monorepo-de-referencia (backend):** una sola tabla, un endpoint principal (`POST /api/search`) + `GET /api/health`. Sin JWT, sin multi-tag, sin webhooks. Foco: rigor de tipos, ejemplos, error envelopes, descripciones útiles.

---

## Misión

Garantizar que la spec OpenAPI:

1. Tenga `info.title`, `info.description`, `info.version`, `info.contact`, `info.license` poblados.
2. Cada endpoint tenga **un único tag descriptivo** registrado en `app/routes.py (TAGS_METADATA dict al inicio)`.
3. Cada endpoint tenga `summary`, `description` (≥2 frases útiles), `operationId` legible.
4. Cada endpoint tenga `response_model` Pydantic con ejemplos (`json_schema_extra={"examples": [...]}`).
5. **Todos los códigos de error** del catálogo (`EMPTY_QUERY`, `LLM_TIMEOUT`, `LLM_INVALID_OUTPUT`, `SQL_NOT_SELECT`, `SQL_FORBIDDEN_TABLE`, `DB_ERROR`, `LLM_UNAVAILABLE`) estén documentados con `responses={400: ..., 422: ..., 500: ..., 503: ...}` y un envelope consistente.
6. Schemas con `Field(..., description=..., examples=[...])`.
7. Sin endpoints "huérfanos" (sin response_model o tag).
8. Sin tipos `Any`, `dict`, `list[Any]` en signatures públicas.
9. Que `app.openapi()` se serialice sin errores y `static/openapi.json` quede actualizado en `backend-developer/`.

---

## Procedimiento (autónomo, iterativo)

### Paso 1 — Snapshot inicial
```bash
cd backend
source venv/bin/activate
python -c "import json,importlib; m=importlib.import_module('app.main'); print(json.dumps(m.app.openapi(), indent=2))" \
  > /tmp/openapi_before.json
```

### Paso 2 — Inventario de endpoints
```bash
grep -rn "@router\." app/routes.py | tee /tmp/endpoints.txt
```
Resultado esperado (audit-friendly):
- `POST /api/search` (router_search)
- `GET /api/health` (router_health)

### Paso 3 — Auditoría por endpoint

Para cada endpoint, verificar y corregir:

| Check | Cómo verificar | Fix si falla |
|---|---|---|
| Tag registrado | `tags=["..."]` aparece en `app/routes.py (TAGS_METADATA dict al inicio)::TAGS_METADATA` | Añadir tag con descripción |
| `summary` presente | `@router.post(..., summary="...")` | Agregar summary (≤80 chars) |
| `description` ≥2 frases | docstring del endpoint | Expandir docstring |
| `response_model` presente | `response_model=SearchResponse` | Crear schema en `app/schemas.py` |
| `responses=` para errores | catálogo completo | Mapear cada `code` del PDF |
| `operationId` legible | `operation_id="searchProperties"` | Renombrar |
| Schema con ejemplos | `model_config = ConfigDict(json_schema_extra=...)` | Inyectar ejemplos del PDF |

### Paso 4 — Verificación de schemas
```bash
python -c "
from app.schemas.search import SearchRequest, SearchResponse, ErrorResponse
import json
print(json.dumps(SearchRequest.model_json_schema(), indent=2))
print(json.dumps(SearchResponse.model_json_schema(), indent=2))
"
```
Cada schema debe tener:
- `title` y `description` a nivel modelo.
- `description` y `examples` por campo.
- Constraints visibles (`min_length`, `max_length`, `ge`, `le`).

### Paso 5 — Re-snapshot y diff
```bash
python -c "import json,importlib; m=importlib.import_module('app.main'); print(json.dumps(m.app.openapi(), indent=2))" \
  > /tmp/openapi_after.json
diff /tmp/openapi_before.json /tmp/openapi_after.json | head -200
```

### Paso 6 — Sincronizar al sitio de docs
```bash
cp /tmp/openapi_after.json ../backend-developer/static/openapi.json
cd ../backend-developer
pnpm build  # falla si la spec rompe el render Scalar
```

---

## Reglas de naming (heredadas del monorepo)

- **operationId:** verbo + sustantivo (`searchProperties`, `getHealth`).
- **Tag:** corto, action-oriented (`Property Search`, `API Status`).
- **Schemas:** `<Domain><Verb>Request|Response` o `<DomainOut|In>` (`SearchRequest`, `SearchResponse`, `PropertyOut`).
- **Error code:** `SCREAMING_SNAKE_CASE` corto y autodescriptivo.

---

## Checklist final (auditable)

- [ ] `app/routes.py (TAGS_METADATA dict al inicio)` documenta cada tag usado.
- [ ] `POST /api/search` y `GET /api/health` tienen `summary`, `description`, `operationId`, `response_model`, `responses` para los 4 códigos HTTP del catálogo (200, 400/422, 500, 503).
- [ ] `SearchRequest` valida `query` con `min_length=1, max_length=500`.
- [ ] `SearchResponse` incluye ejemplo completo.
- [ ] `ErrorResponse` tiene envelope `{error: {code, message, detail?}}`.
- [ ] `static/openapi.json` en docs actualizado y `pnpm build` verde.
- [ ] Diff documentado en `assessments/CHANGELOG.md` bajo `Docs · audit-openapi <fecha>`.

---

## Iteración

Si el diff inicial muestra ≥3 violaciones, **iterar**:
1. Aplicar fixes en lote por archivo (`app/routes.py`, `app/schemas.py*`).
2. Re-snapshot.
3. Repetir hasta diff vacío en violaciones (sólo cambios de mejora).

Al finalizar, **anotar en CHANGELOG.md** la entrada `Docs · OpenAPI audit pass <fecha>` con conteo de fixes aplicados.
