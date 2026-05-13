# proyecto-propiedades

> **Búsqueda de propiedades inmobiliarias en lenguaje natural** — Vue 3 + FastAPI + MySQL + Ollama

Solución al assessment Full Stack. App web que recibe consultas en español (ej. *"Busco casas de 3 habitaciones en zona 10"*), las traduce a SQL vía LLM local, las valida con triple defensa anti‑injection (sanitización + `sqlglot` AST + whitelist) y devuelve resultados JSON al frontend Vue.

---

## 🔗 Entregables (abre tras `docker compose up -d --build`)

| Entregable | URL |
|---|---|
| **UI Vue** (app principal) | <http://localhost:8080> |
| **Developer site** (Docusaurus + Scalar, bonus) | <http://localhost:3001> |
| **Swagger UI** (API interactiva) | <http://localhost:8000/docs> |
| **ReDoc** (API legible) | <http://localhost:8000/redoc> |

```bash
open http://localhost:8080        # UI Vue
open http://localhost:3001        # Developer site
open http://localhost:8000/docs   # Swagger UI
open http://localhost:8000/redoc  # ReDoc
```

**Repositorio:** <https://github.com/braianstaimer/proyecto-propiedades>

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org)
[![Vue](https://img.shields.io/badge/Vue-3.5-42b883.svg)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg)](https://www.mysql.com)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

---

## 🚀 Quickstart

### 1. Pre-requisitos

- Docker + Docker Compose v2
- Ollama corriendo en el **host** con `llama3.2:3b`:

  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ollama pull llama3.2:3b
  ollama serve
  ```

### 2. Levantar el stack

```bash
cp .env.example .env              # opcional, hay defaults
docker compose up -d --build      # 4 contenedores healthy en ~30s
```

Esto arranca **4 servicios**: `mysql`, `backend`, `frontend` (nginx), `docs` (developer site).

### 3. Verificar que todo está arriba

```bash
docker compose ps                 # los 4 contenedores en estado (healthy)
curl http://localhost:8000/api/health
# → { "status":"ok", "db":"ok", "llm":"ok", "version":"0.1.0" }
```

### 4. Probar una búsqueda

Desde la UI: abre <http://localhost:8080> y escribe la consulta.

Desde curl:

```bash
curl -X POST http://localhost:8000/api/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"Busco casas de 3 habitaciones en zona 10"}' | jq
```

---

## 🧪 Las 6 búsquedas del PDF

| # | Consulta | Resultados esperados (seed) |
|---|---|---|
| 1 | "Busco casas de 3 habitaciones en zona 10" | 2 |
| 2 | "Muéstrame departamentos de menos de $150,000" | 4 |
| 3 | "Propiedades con más de 2 baños y al menos 150 metros cuadrados" | 5 |
| 4 | "Casas publicadas en los últimos 30 días" | depende de fecha actual |
| 5 | "Terrenos en venta con precio entre $50,000 y $100,000" | 3 |
| 6 | "Departamentos con 2 habitaciones en zona 15" | 2 |

Las 6 retornan **≥ 1 resultado**. Ver evidencia en [Developer site → `/intro`](http://localhost:3001/intro).

---

## 🏗 Stack

| Capa | Tecnología |
|---|---|
| Frontend | Vue 3.5 (Composition API) + TypeScript + Vite + Pinia + Tailwind 3 |
| Backend | FastAPI 0.115 (Python 3.12) + SQLAlchemy 2 async + aiomysql |
| Validación SQL | `sqlglot` AST + whitelist (triple defensa anti‑injection) |
| LLM | Ollama (host:11434) · `llama3.2:3b` |
| BD | MySQL 8.0 |
| Orquestación | Docker Compose v2 |
| Developer site (bonus) | Docusaurus 3.8 + `@scalar/docusaurus` |
| Tests backend | pytest + pytest-asyncio + httpx-mock — **187 tests, 96% coverage** |
| Tests frontend | vitest + happy-dom + @vue/test-utils — **38 tests, 94% coverage** |

---

## 📦 Subproyectos

Cada subproyecto tiene su propio README con instrucciones detalladas:

| Subproyecto | Path | Detalles |
|---|---|---|
| Backend (FastAPI) | [`backend/`](./backend/README.md) | API `POST /api/search`, validador SQL, integración Ollama |
| Frontend (Vue 3) | [`frontend/`](./frontend/README.md) | SPA con grid responsive, estados loading/error/empty |
| Developer site (bonus) | [`backend-developer/`](./backend-developer/README.md) | Docs interactivas con Scalar |
| Scripts | [`backend/scripts/`](./backend/scripts/README.md) | Scraper opcional de `mapainmueble.com` |

### Backend — `backend/`

FastAPI 0.115 sobre Python 3.12. Endpoint `POST /api/search` traduce NL → SQL vía Ollama, valida con `sqlglot` AST + whitelist y ejecuta sobre la tabla `propiedades`.

Dev nativo con hot reload:

```bash
docker compose up -d mysql        # sólo la DB
cd backend
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
DB_HOST=localhost uvicorn app.main:app --reload --port 8000
```

| Método | Path | Descripción |
|---|---|---|
| POST | `/api/search` | Traduce NL → SQL → resultados |
| GET | `/api/health` | Estado DB + LLM |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |
| GET | `/openapi.json` | Spec OpenAPI 3.1 |

### Frontend — `frontend/`

Vue 3.5 (Composition API) + TypeScript + Vite + Pinia + Tailwind 3. SPA con grid responsive, estados loading/error/empty y toggle "Mostrar SQL generado".

Dev nativo con HMR (Vite):

```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev                       # → http://localhost:5173
```

| Componente | Rol |
|---|---|
| `SearchBar.vue` | Input con placeholder rotativo + botón Buscar |
| `PropertyCard.vue` | Card individual con chips (tipo, hab, baños, m²) |
| `PropertyGrid.vue` | Grid responsive (3/2/1 cols) |
| `EmptyState.vue` | Sin resultados con sugerencia útil |
| `ErrorAlert.vue` | Banda dismissible con `error.code` humanizado |
| `LoadingSpinner.vue` | Skeleton cards animadas |
| `SqlPreview.vue` | Bloque `<pre>` con el SQL generado (toggle) |
| `AppHeader.vue` | Header con toggle SQL |

### Developer site (bonus) — `backend-developer/`

Documentación del API con referencia interactiva Scalar (prueba endpoints desde el browser), guías de flujo y catálogo de errores. **Levanta automático** como contenedor `docs` con `docker compose up -d --build`.

Dev nativo (hot reload):

```bash
cd backend-developer
npm install
# Opcional: refrescar spec desde el backend vivo
OPENAPI_URL=http://localhost:8000/openapi.json node scripts/fetch-openapi.mjs
npm start                         # → http://localhost:3001
# o build estático: npm run build && npm run serve
```

**Rutas servidas en <http://localhost:3001>:**

| Ruta | Contenido |
|---|---|
| `/intro` | Quickstart + curl examples + 6 búsquedas demo |
| `/flows/search-flow` | Sequence diagram del pipeline NL → SQL |
| `/architecture/error-codes` | Catálogo de 13 códigos de error |
| `/reference/health` | Documentación de `GET /api/health` |
| `/api-reference` | Scalar UI interactiva sobre el OpenAPI 3.1 |

### Scripts — `backend/scripts/scrape_mapainmueble.py`

Scraper opcional del sitemap de [mapainmueble.com](https://mapainmueble.com/sitemap.xml). Descarga fichas, parsea JSON‑LD (`schema.org/RealEstateListing`) y carga filas nuevas en la tabla `propiedades` con dedupe `INSERT IGNORE` + `UNIQUE (titulo, ubicacion)`. Por defecto **sólo ingiere ventas**.

```bash
# Dry-run (5 fichas, no escribe)
docker compose exec backend python -m scripts.scrape_mapainmueble --dry-run --limit 5

# Ingest real
docker compose exec backend python -m scripts.scrape_mapainmueble --limit 100
```

| Flag | Default | Descripción |
|---|---|---|
| `--limit N` | (todas) | Recorta a las primeras N URLs del sitemap |
| `--concurrency N` | 6 | Fetchs HTTP simultáneos (≤ 10) |
| `--batch-size N` | 50 | Filas por `INSERT IGNORE` |
| `--dry-run` | false | No escribe en MySQL |
| `--include-alquiler` | false | Incluye alquileres (default: solo ventas) |
| `--log-level` | INFO | `DEBUG \| INFO \| WARNING \| ERROR` |

Es **idempotente**: una segunda corrida con el mismo `--limit` reporta `skipped_existing ≈ fetched`. Detalle en [`backend/scripts/README.md`](./backend/scripts/README.md).

---

## 🛡 Seguridad: triple defensa anti‑injection

1. **Sanitización de entrada** — trim, len ≤ 500, control chars rechazados.
2. **Prompt + LLM** — temperature 0.0, few‑shot con esquema, timeout 15 s.
3. **Validación SQL con `sqlglot` AST + whitelist**:
   - 1 sólo `SELECT` (multi‑statement rechazado)
   - Tabla única `propiedades`
   - Sin DML/DDL/grants
   - Sin `SLEEP`/`BENCHMARK`/`LOAD_FILE`/`INTO OUTFILE`
   - `LIMIT` clamp a 200
4. **(Opcional)** Usuario `appuser_ro` con sólo `GRANT SELECT` — activar en `docker-compose.override.yml`.

---

## 📡 Catálogo de errores API

Envelope estándar:

```json
{ "error": { "code": "...", "message": "...", "detail": null, "request_id": "..." } }
```

| HTTP | `error.code` |
|---|---|
| 422 | `EMPTY_QUERY`, `LLM_TIMEOUT`, `LLM_INVALID_OUTPUT`, `SQL_NOT_SELECT`, `SQL_FORBIDDEN_TABLE`, `SQL_FORBIDDEN_STATEMENT`, `SQL_DANGEROUS_FUNCTION` |
| 429 | `RATE_LIMIT` (opt‑in) |
| 500 | `DB_ERROR` |
| 503 | `LLM_UNAVAILABLE` |

Detalle por código: [Developer site → `/architecture/error-codes`](http://localhost:3001/architecture/error-codes).

---

## 🧪 Tests

### Backend

```bash
cd backend
source venv/bin/activate

pytest                      # 187 tests (unit + integration + contract + smoke)
pytest --cov=app            # con cobertura
pytest -m smoke             # sólo golden path (13 tests)
```

### Frontend

```bash
cd frontend
npm run test:ci             # 38 tests con cobertura
npm run test:smoke          # sólo golden path (6 tests)
npm run typecheck           # vue-tsc --noEmit
```

---

## 📊 Métricas

| Métrica | Target | Actual |
|---|---|---|
| Backend tests | — | **187 verdes** |
| Backend coverage global | ≥ 80% | **96%** ✓ |
| Backend coverage `sql_validator` | ≥ 95% | **97%** ✓ |
| Frontend tests | — | **38 verdes** |
| Frontend coverage | — | **94%** |
| Cold start `docker compose up -d --build` (4 servicios) | ≤ 90 s | **~30 s** ✓ |
| p50 `/api/search` | ≤ 8 s | **~1.5 s** (caliente) ✓ |
| Las 6 búsquedas PDF retornan ≥ 1 | 6/6 | **6/6** ✓ |
| ruff / mypy / lizard / vue-tsc / build | PASS | **PASS** ✓ |

---

## 📁 Estructura

```
proyecto-propiedades/
├── README.md                     ← Este archivo
├── docker-compose.yml            ← mysql + backend + frontend + docs
├── docker-compose.override.yml   ← Hardenings opcionales (healthchecks, RO, charset)
├── .env.example
│
├── frontend/                     ← Vue 3 SPA               → :8080
├── backend/                      ← FastAPI                 → :8000
│   ├── app/                      ← código de la app
│   ├── persistencia/             ← DDL + seed + migrations
│   ├── scripts/                  ← scraper opcional
│   └── tests/                    ← 187 tests
├── backend-developer/            ← Docusaurus + Scalar     → :3001
└── .claude/commands/             ← Slash commands (audits + syncs)
```

---

## 🤖 Slash commands (`.claude/commands/`)

Comandos versionados para automatizar audits y syncs:

| Comando | Uso |
|---|---|
| `/audit-openapi` | Audita la spec OpenAPI (info, tags, schemas, examples, errores) |
| `/code-review` | Audit pre‑merge: dead code, patterns, coverage, gates |
| `/contract-check` | Verifica sync backend ↔ types frontend ↔ docs spec |
| `/sync-api-docs` | Hidrata `backend-developer/static/openapi.json` desde el backend vivo |
| `/test-audit` | Auditor de tests con foco en cobertura crítica (`sql_validator` ≥ 95%) |

---

## 🩺 Troubleshooting

| Síntoma | Fix |
|---|---|
| `ConnectionRefusedError` a MySQL | Esperar `(healthy)` o usar el override (incluye `condition: service_healthy`) |
| 503 `LLM_UNAVAILABLE` | Verificar `ollama serve` y que `ollama list` incluya `llama3.2:3b` |
| Linux: `host.docker.internal` no resuelve | El override añade `extra_hosts: host-gateway` |
| `SHOW TABLES` vacío | `docker compose down -v && docker compose up -d` |
| MySQL falla con "password not specified" | El compose toma defaults; si no, `cp .env.example .env` |
| `npm install` falla en `backend-developer` | Usar Node 20 LTS (`nvm use 20`) — Docusaurus 3.8 no soporta Node 24+ |

---

## 🎬 Video demo

_Pendiente — link al cierre._

## 📄 License

MIT
