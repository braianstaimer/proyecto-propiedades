# proyecto-propiedades

> **Búsqueda de propiedades inmobiliarias en lenguaje natural** — Vue 3 + FastAPI + MySQL + Ollama

Solución al assessment Full Stack. App web que recibe consultas en español natural (ej. *"Busco casas de 3 habitaciones en zona 10"*), las traduce a SQL via LLM local, valida con triple defensa anti-injection (sanitización + `sqlglot` AST + whitelist) y devuelve resultados JSON al frontend Vue.

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org)
[![Vue](https://img.shields.io/badge/Vue-3.5-42b883.svg)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg)](https://www.mysql.com)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

**Repo:** https://github.com/braianstaimer/proyecto-propiedades

---

## 🚀 Quickstart

### Pre-requisitos

- Docker + Docker Compose v2
- Ollama corriendo en el host con `llama3.2:3b`:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ollama pull llama3.2:3b
  ollama serve
  ```

### Levantar la app

```bash
cp .env.example .env              # opcional, hay defaults
docker compose up -d --build      # 4 contenedores healthy en ~30s
```

### Verificar

```bash
docker compose ps                 # mysql + backend + frontend + docs (healthy)
curl http://localhost:8000/api/health
# { "status":"ok", "db":"ok", "llm":"ok", "version":"0.1.0" }

open http://localhost:8080        # UI Vue
open http://localhost:3001        # Developer site (Docusaurus + Scalar)
open http://localhost:8000/docs   # Swagger UI
open http://localhost:8000/redoc  # ReDoc
```

### Probar una búsqueda

```bash
curl -X POST http://localhost:8000/api/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"Busco casas de 3 habitaciones en zona 10"}' | jq
```

---

## 🧪 Las 6 búsquedas del PDF

| # | Consulta | Count esperado (seed) |
|---|---|---|
| 1 | "Busco casas de 3 habitaciones en zona 10" | 2 |
| 2 | "Muéstrame departamentos de menos de $150,000" | 4 |
| 3 | "Propiedades con más de 2 baños y al menos 150 metros cuadrados" | 5 |
| 4 | "Casas publicadas en los últimos 30 días" | depende de fecha actual |
| 5 | "Terrenos en venta con precio entre $50,000 y $100,000" | 3 |
| 6 | "Departamentos con 2 habitaciones en zona 15" | 2 |

---

## 📚 Documentación

| Recurso | URL | Cómo levantarlo |
|---|---|---|
| **API Swagger UI** | http://localhost:8000/docs | Incluido en el stack del backend |
| **API ReDoc** | http://localhost:8000/redoc | Incluido en el stack del backend |
| **OpenAPI 3.1 spec** | http://localhost:8000/openapi.json | Incluido en el stack del backend |
| **Developer site** (BONUS, Docusaurus + Scalar) | http://localhost:3001 | Incluido en el stack del compose root |

### Sitio para desarrolladores (`backend-developer/`)

Documentación del API con referencia interactiva Scalar (prueba endpoints desde el browser), guías de flujo y catálogo de errores. Levanta como contenedor `docs` junto al resto del stack en `docker compose up -d --build`.

Para desarrollo nativo del sitio (hot reload):

```bash
cd backend-developer
npm install
# Opcional: refrescar spec desde el backend vivo (recomendado tras cambios)
OPENAPI_URL=http://localhost:8000/openapi.json node scripts/fetch-openapi.mjs
npm start                         # dev server en http://localhost:3001
# o build estático:
npm run build && npm run serve    # http://localhost:3001
```

**Rutas servidas:**

| Ruta | Contenido |
|---|---|
| `/intro` | Quickstart + curl examples + 6 búsquedas demo |
| `/flows/search-flow` | Sequence diagram del pipeline NL → SQL |
| `/architecture/error-codes` | Catálogo de 13 códigos de error (10 server + 3 client) |
| `/reference/health` | Documentación de `GET /api/health` |
| `/api-reference` | Scalar UI interactiva sobre el OpenAPI 3.1 |

Detalle completo en [`backend-developer/README.md`](./backend-developer/README.md).

---

## 📁 Estructura

```
proyecto-propiedades/
├── README.md                     ← Este archivo
├── docker-compose.yml            ← Orquestador (mysql + backend + frontend + docs)
├── docker-compose.override.yml   ← Hardenings opcionales (healthchecks, RO, charset)
├── .env.example
├── .gitignore
├── .claude/commands/             ← Slash commands (audit-openapi, code-review,
│                                    contract-check, sync-api-docs, test-audit)
│
├── frontend/                     ← Vue 3 SPA
│   ├── src/
│   │   ├── components/           ← SearchBar, PropertyCard, PropertyGrid,
│   │   │                            EmptyState, ErrorAlert, LoadingSpinner,
│   │   │                            SqlPreview, AppHeader
│   │   ├── views/SearchView.vue
│   │   ├── stores/search.ts      ← Pinia
│   │   ├── composables/useSearch.ts
│   │   ├── services/api.ts       ← axios + ApiError envelope
│   │   ├── types/api.ts          ← regenerable desde openapi.json
│   │   ├── App.vue
│   │   └── main.ts
│   ├── tests/
│   │   ├── unit/                 ← vitest + happy-dom
│   │   └── smoke/                ← golden path · `npm run test:smoke`
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── README.md
│
├── backend/                      ← FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               ← lifespan + middleware + handlers
│   │   ├── routes.py             ← /api/search, /api/health
│   │   ├── schemas.py            ← Pydantic DTOs
│   │   ├── repositories.py       ← Repository ABC + MySQL + InMemory
│   │   ├── search_service.py     ← Orquestador (Pipes & Filters)
│   │   ├── llm_service.py        ← LLMProvider Protocol + Ollama + Mock
│   │   ├── sql_validator.py      ← sqlglot AST + whitelist
│   │   ├── prompts.py            ← PROMPT_VERSION=v1 + few-shot
│   │   ├── config.py             ← Pydantic Settings + @lru_cache
│   │   ├── exceptions.py         ← 10 errores tipados
│   │   ├── database.py           ← DataSource ABC + MySQLDataSource
│   │   └── dependencies.py       ← Annotated[T, Depends(...)] factories
│   ├── persistencia/
│   │   ├── 01_schema.sql         ← DDL idempotente (IF NOT EXISTS)
│   │   ├── 02_seed_data.sql      ← 20 filas (INSERT IGNORE + UNIQUE)
│   │   └── runner.py             ← run_migrations_if_needed() (lifespan)
│   ├── scripts/                  ← (opcional) scrape_mapainmueble.py
│   ├── tests/
│   │   ├── unit/                 ← 96 tests (validator, llm, service, ...)
│   │   ├── integration/          ← 25 tests con MySQL real
│   │   ├── contract/             ← 17 tests (LSP cross-impl + OpenAPI snapshot)
│   │   └── smoke/                ← 13 tests · `pytest -m smoke`
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml            ← ruff + mypy + pytest + coverage
│   └── README.md
│
└── backend-developer/            ← BONUS · Docusaurus 3.8 + @scalar/docusaurus
    ├── docs/
    │   ├── intro.md
    │   ├── flows/search-flow.md
    │   ├── architecture/error-codes.md
    │   └── reference/health.md
    ├── static/openapi.json       ← spec versionado · refresh con fetch-openapi.mjs
    ├── scripts/fetch-openapi.mjs
    ├── docusaurus.config.ts
    ├── package.json
    ├── Dockerfile                ← build estático + nginx :3001
    ├── nginx.conf
    └── README.md
```

---

## 🏗 Stack

| Capa | Tecnología |
|---|---|
| Frontend | Vue 3.5 (Composition API) + TS + Vite + Pinia + Tailwind 3 |
| Backend | FastAPI 0.115 (Python 3.12) + SQLAlchemy 2 async + aiomysql |
| Validación | `sqlglot` AST whitelist (triple defensa anti-injection) |
| LLM | Ollama (host:11434) · `llama3.2:3b` |
| BD | MySQL 8.0 |
| Orquestación | Docker Compose v2 (baseline PDF + override opcional) |
| Docs site (bonus) | Docusaurus 3.8 + `@scalar/docusaurus` |
| Tests backend | pytest + pytest-asyncio + httpx-mock (151 tests) |
| Tests frontend | vitest + happy-dom + @vue/test-utils (26 tests) |

---

## 📡 Endpoints API

| Método | Path | Descripción |
|---|---|---|
| POST | `/api/search` | Traduce NL → SQL → resultados |
| GET | `/api/health` | Estado DB + LLM |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |
| GET | `/openapi.json` | Spec OpenAPI 3.1 |

Catálogo de errores tipados:

| HTTP | `error.code` |
|---|---|
| 422 | `EMPTY_QUERY`, `LLM_TIMEOUT`, `LLM_INVALID_OUTPUT`, `SQL_NOT_SELECT`, `SQL_FORBIDDEN_TABLE`, `SQL_FORBIDDEN_STATEMENT`, `SQL_DANGEROUS_FUNCTION` |
| 429 | `RATE_LIMIT` (opt-in) |
| 500 | `DB_ERROR` |
| 503 | `LLM_UNAVAILABLE` |

Envelope:

```json
{ "error": { "code": "...", "message": "...", "detail": null, "request_id": "..." } }
```

Detalle en [Developer site → `/architecture/error-codes`](http://localhost:3001/architecture/error-codes).

---

## 🧪 Tests

### Backend

```bash
cd backend
source venv/bin/activate

pytest                      # 187 tests (unit + integration + contract + smoke)
pytest --cov=app            # con cobertura
pytest -m smoke             # sólo golden path para release (13 tests)
pytest tests/unit           # sólo unit
pytest tests/integration    # con MySQL real
```

### Frontend

```bash
cd frontend
npm run test:ci             # 26 tests con cobertura
npm run test:smoke          # sólo golden path (6 tests)
npm run typecheck           # vue-tsc --noEmit
```

---

## 🛡 Seguridad: triple defensa anti-injection

1. **Sanitización entrada** — trim, len ≤ 500, control chars rechazados
2. **Prompt + LLM** — temp 0.0, few-shot con esquema, timeout 15s
3. **`sqlglot` AST + whitelist**:
   - 1 sólo `SELECT` (multi-statement rechazado)
   - Tabla única `propiedades`
   - Sin DML/DDL/grants
   - Sin `SLEEP`/`BENCHMARK`/`LOAD_FILE`/`INTO OUTFILE`
   - `LIMIT` clamp a 200
4. **(opcional, hardening)** Usuario `appuser_ro` con sólo `GRANT SELECT` — activar en `docker-compose.override.yml`

---

## 📊 Métricas

| Métrica | Target | Actual |
|---|---|---|
| Backend tests | — | **187 verdes** |
| Backend coverage global | ≥ 80% | **96%** ✓ |
| Backend coverage `sql_validator` | ≥ 95% | **97%** ✓ |
| Frontend tests | — | **26 verdes** |
| Frontend coverage | — | **91%** |
| Cold-start `docker compose up -d --build` (4 servicios) | ≤ 90s | **~30s** ✓ |
| p50 `/api/search` | ≤ 8s | **~1.5s** (caliente) ✓ |
| Las 6 búsquedas PDF retornan ≥ 1 | 6/6 | **6/6** ✓ |
| ruff / mypy / lizard / vue-tsc / build | PASS | **PASS** ✓ |

---

## 🛠 Dev nativo (sin Docker para backend/frontend)

```bash
# Sólo MySQL (vía docker)
docker compose up -d mysql

# Backend con hot-reload
cd backend
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
DB_HOST=localhost uvicorn app.main:app --reload --port 8000

# Frontend con Vite HMR
cd ../frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev                       # http://localhost:5173

# (opcional) Developer site
cd ../backend-developer
npm install && npm start          # http://localhost:3001
```

READMEs por subproyecto para detalle:
- [`backend/README.md`](./backend/README.md)
- [`frontend/README.md`](./frontend/README.md)
- [`backend-developer/README.md`](./backend-developer/README.md)

---

## 🤖 Slash commands (`.claude/commands/`)

Comandos versionados para automatizar audits y syncs:

| Comando | Uso |
|---|---|
| `/audit-openapi` | Audita la spec OpenAPI (info, tags, schemas, examples, errores) |
| `/code-review` | Audit pre-merge: dead code, patterns, anti-patterns, coverage, gates |
| `/contract-check` | Verifica sync backend ↔ types frontend ↔ docs spec |
| `/sync-api-docs` | Hidrata `backend-developer/static/openapi.json` desde el backend vivo |
| `/test-audit` | Auditor de tests con foco en cobertura crítica (`sql_validator` ≥95%) |

---

## 🩺 Troubleshooting

| Síntoma | Fix |
|---|---|
| `ConnectionRefusedError` a mysql | Esperar `(healthy)` o usar override (incluye `condition: service_healthy`) |
| 503 `LLM_UNAVAILABLE` | Verificar `ollama serve` y que `ollama list` contenga `llama3.2:3b` |
| Linux: `host.docker.internal` no resuelve | El override añade `extra_hosts: host-gateway` |
| `SHOW TABLES` vacío | `docker compose down -v && docker compose up -d` |
| MySQL falla con "password not specified" | El compose toma defaults; si no, `cp .env.example .env` |
| `npm install` falla en `backend-developer` | Usar Node 20 LTS (`nvm use 20`) — Docusaurus 3.8 no soporta Node 24+ todavía |

---

## 🎬 Video demo

_Pendiente — link al cierre._

## 📄 License

MIT
