# proyecto-propiedades

> **Búsqueda de propiedades inmobiliarias en lenguaje natural** — Vue 3 + FastAPI + MySQL + Ollama

Solución al assessment Full Stack. App web que recibe consultas en español natural (ej. *"Busco casas de 3 habitaciones en zona 10"*), las traduce a SQL via LLM local, valida con triple defensa anti-injection (sanitización + `sqlglot` AST + whitelist) y devuelve resultados JSON al frontend Vue.

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org)
[![Vue](https://img.shields.io/badge/Vue-3.5-42b883.svg)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg)](https://www.mysql.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

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
cp .env.example .env
docker compose up -d --build      # 3 servicios healthy en ~40s
```

### Verificar

```bash
docker compose ps                 # 3 contenedores healthy
curl http://localhost:8000/api/health
# { "status":"ok", "db":"ok", "llm":"ok", "version":"0.1.0" }

open http://localhost:8080        # UI Vue
```

### Probar una búsqueda

```bash
curl -X POST http://localhost:8000/api/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"Busco casas de 3 habitaciones en zona 10"}' | jq
```

---

## 🧪 Las 6 búsquedas del PDF

| # | Consulta | Count esperado |
|---|---|---|
| 1 | "Busco casas de 3 habitaciones en zona 10" | 2 |
| 2 | "Muéstrame departamentos de menos de $150,000" | 4 |
| 3 | "Propiedades con más de 2 baños y al menos 150 metros cuadrados" | 5 |
| 4 | "Casas publicadas en los últimos 30 días" | 5 |
| 5 | "Terrenos en venta con precio entre $50,000 y $100,000" | 3 |
| 6 | "Departamentos con 2 habitaciones en zona 15" | 2 |

---

## 📁 Estructura

```
proyecto-propiedades/
├── README.md                     ← Este archivo
├── docker-compose.yml            ← Orquestador (mysql + backend + frontend)
├── docker-compose.override.yml   ← Hardenings opcionales (healthchecks, RO, charset)
├── .env.example
├── .gitignore
│
├── frontend/                     ← Vue 3 SPA
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── App.vue
│   │   └── main.ts
│   ├── tests/unit/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── README.md
│
├── backend/                      ← FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── llm_service.py
│   │   └── (extras: schemas, repositories, search_service, sql_validator, ...)
│   ├── persistencia/
│   │   ├── 01_schema.sql
│   │   ├── 02_seed_data.sql
│   │   └── runner.py
│   ├── tests/{unit,integration,contract}/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
│
└── backend-developer/            ← BONUS · Docusaurus 3.8 + @scalar/docusaurus
    ├── docs/{intro,flows,architecture,reference}/
    ├── static/openapi.json
    ├── docusaurus.config.ts
    └── ...
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
| Docs (bonus) | Docusaurus 3.8 + `@scalar/docusaurus` |

---

## 📡 Endpoints

| Método | Path | Descripción |
|---|---|---|
| POST | `/api/search` | Traduce NL → SQL → resultados |
| GET | `/api/health` | Estado DB + LLM |
| GET | `/docs` | Swagger UI |
| GET | `/openapi.json` | Spec OpenAPI 3.1 |

---

## 🧪 Tests

```bash
# Backend (138 tests, 96% cobertura)
cd backend && pytest --cov=app

# Frontend (20 tests, 91.6% cobertura)
cd frontend && npm run test:ci
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
4. **(opcional, hardening)** Usuario `appuser_ro` con sólo `GRANT SELECT`

---

## 📊 Métricas

| Métrica | Target | Actual |
|---|---|---|
| Backend coverage global | ≥ 80% | **96.26%** ✓ |
| Backend coverage `sql_validator` | ≥ 95% | **97%** ✓ |
| Backend tests | — | **138 verdes** |
| Frontend coverage | — | **91.6%** |
| Frontend tests | — | **20 verdes** |
| Cold-start `docker compose up -d --build` | ≤ 90s | **~40s** ✓ |
| p50 `/api/search` | ≤ 8s | **~1.5s** (caliente) ✓ |
| 6 búsquedas PDF retornan ≥ 1 | 6/6 | **6/6** ✓ |

---

## 🛠 Dev nativo (sin Docker para backend/frontend)

```bash
# Sólo MySQL
docker compose up -d mysql

# Backend
cd backend
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
DB_HOST=localhost uvicorn app.main:app --reload --port 8000

# Frontend (Vite HMR)
cd ../frontend
npm install && npm run dev    # :5173
```

Ver READMEs específicos por proyecto para más detalle.

---

## 🩺 Troubleshooting

| Síntoma | Fix |
|---|---|
| `ConnectionRefusedError` a mysql | Esperar `(healthy)` o usar override (incluye `condition: service_healthy`) |
| 503 `LLM_UNAVAILABLE` | Verificar `ollama serve` y `ollama list` |
| Linux: `host.docker.internal` no resuelve | El override añade `extra_hosts: host-gateway` |
| `SHOW TABLES` vacío | `docker compose down -v && docker compose up -d` |

---

## 🎬 Video demo

_Pendiente — link al cierre._

## 📄 License

MIT
