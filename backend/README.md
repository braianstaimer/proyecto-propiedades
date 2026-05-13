# proyecto-propiedades · Backend

> **API REST** — FastAPI 0.115 + Python 3.12 + SQLAlchemy 2 async + MySQL 8 + Ollama (`llama3.2:3b`)

Endpoint `POST /api/search` que traduce consultas en español natural a SQL via LLM local, valida con `sqlglot` AST + whitelist (triple defensa anti-injection) y ejecuta sobre la tabla `propiedades`.

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

---

## 🚀 Levantar la app

El orquestador vive en el root del proyecto (`proyecto-propiedades/`). Ver el [README root](../README.md).

```bash
cd ..                              # al root del proyecto
cp .env.example .env
docker compose up -d --build       # mysql + backend + frontend
```

## 🛠 Dev nativo (sólo backend, con hot-reload)

```bash
# 1. Sólo MySQL via el compose root
cd .. && docker compose up -d mysql

# 2. venv + deps
cd backend
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. uvicorn con hot-reload (apunta a MySQL en localhost)
DB_HOST=localhost uvicorn app.main:app --reload --port 8000
```

---

## 📡 API

| Método | Path | Descripción | Body |
|---|---|---|---|
| POST | `/api/search` | Traduce NL → SQL → resultados | `{"query": "Busco casas..."}` |
| GET | `/api/health` | Estado DB + LLM | — |
| GET | `/docs` | Swagger UI | — |
| GET | `/openapi.json` | OpenAPI 3.1 spec | — |

### Ejemplo `curl`

```bash
curl -X POST http://localhost:8000/api/search \
  -H 'Content-Type: application/json' \
  -H 'X-Request-ID: demo-001' \
  -d '{"query":"Busco casas de 3 habitaciones en zona 10"}' | jq
```

Respuesta:

```json
{
  "query": "Busco casas de 3 habitaciones en zona 10",
  "sql": "SELECT id, titulo, ... FROM propiedades WHERE tipo = 'casa' AND habitaciones = 3 AND LOWER(ubicacion) LIKE '%zona 10%' LIMIT 50",
  "count": 2,
  "results": [ /* ... */ ],
  "took_ms": 1820
}
```

### Las 6 búsquedas del assessment

1. `"Busco casas de 3 habitaciones en zona 10"` → count=2
2. `"Muéstrame departamentos de menos de $150,000"` → count=4
3. `"Propiedades con más de 2 baños y al menos 150 metros cuadrados"` → count=5
4. `"Casas publicadas en los últimos 30 días"` → count=5
5. `"Terrenos en venta con precio entre $50,000 y $100,000"` → count=3
6. `"Departamentos con 2 habitaciones en zona 15"` → count=2

---

## 🏗 Arquitectura

```
HTTP (routes.py)
     ↓
Search Service (search_service.py · orquestador)
     ↓                        ↓                       ↓
LLM Provider           SQL Validator         Property Repository
(llm_service.py)       (sql_validator.py)    (repositories.py)
  ↓                                              ↓
Ollama HTTP                              SQLAlchemy 2 async
(host:11434)                             aiomysql
                                              ↓
                                         MySQL 8.0
```

### Patrones aplicados

- **Repository (ABC)** + **MySQLPropertyRepository** + **InMemoryPropertyRepository** (tests)
- **Adapter (Protocol)** — `LLMProvider` + `OllamaLLMProvider` + `MockLLMProvider`
- **Factory Method** — `build_llm_provider` / `build_property_repository` por env
- **Strategy** — `SQLValidator` con reglas configurables
- **DI (Annotated)** — FastAPI `Depends` factories
- **DTO ≠ ORM** — Pydantic schemas en `schemas.py`, SQLAlchemy en `models.py`
- **Lifespan + app.state** — construcción + cleanup determinista
- **Pipes & Filters** — `sanitize → llm → validate → execute`

### SOLID (verificable por grep)

```bash
# DIP: SearchService no importa infraestructura
grep -E "import (httpx|aiomysql|sqlalchemy|mysql|ollama)" app/search_service.py
# → vacío ✓
```

### Defensa anti-injection (triple capa)

1. **Sanitización entrada:** trim, len ≤ 500, control chars rechazados
2. **Prompt + LLM:** temp 0.0, few-shot con esquema, timeout 15s
3. **sqlglot AST + whitelist:**
   - 1 sólo `SELECT` (multi-statement → 422)
   - Tabla única `propiedades`
   - Sin DML/DDL
   - Sin `SLEEP`/`BENCHMARK`/`LOAD_FILE`/`INTO OUTFILE`
   - `LIMIT` clamp a 200
4. **(opcional)** MySQL `appuser_ro` con sólo `GRANT SELECT` (ver `docker-compose.override.yml`)

---

## 🔎 Decisión técnica — Búsqueda híbrida con FULLTEXT

### Motivación

Un LLM de 3B parámetros (`llama3.2:3b`, default del assessment) tiende a copiar literalmente palabras del query del usuario al SQL, ignorando el esquema. Caso real:

- Usuario: `"APARTAMENTO SAN ISIDRO 2021"`
- LLM (sin FULLTEXT): `WHERE tipo = 'apartamento' AND LOWER(ubicacion) LIKE '%san isidro%'`
- DB: el row real es `tipo = 'departamento'` (enum canónico). El filtro queda vacío.

Resolverlo en código (post-procesar el SQL, mapear sinónimos en Python, two-pass LLM) rompe la regla "una sola pasada NL→SQL" y agrega complejidad fuera del scope del assessment.

### Implementación

1. **Schema** — índice nativo de MySQL sobre las tres columnas textuales:
   ```sql
   FULLTEXT INDEX ft_search (titulo, descripcion, ubicacion)
   ```
2. **Prompt** — el LLM aprende dos herramientas y cuándo usar cada una:
   - **(A) Filtros estructurados** (`=`, `<`, `BETWEEN`, `DATE_SUB`) sobre columnas tipadas: `tipo`, `precio`, `habitaciones`, `banos`, `area_m2`, `fecha_publicacion`.
   - **(B) FULLTEXT BOOLEAN MODE** sobre texto libre: `MATCH(titulo, descripcion, ubicacion) AGAINST('+t1 +t2 ...' IN BOOLEAN MODE)` + `ORDER BY MATCH(...) DESC` para relevancia.

   Regla de decisión codificada en el prompt: clasifica cada token como `ENUM | ESTRUCTURADO | ZONA | TEXTO_LIBRE` y enruta. Si no hay tokens de texto libre, NO emite MATCH.
3. **Sinónimos del enum** mapeados en el prompt (no en código): `apartamento|depto|depa|piso|flat → departamento`, `finca|lote|parcela → terreno`, `bodega|comercial → local`.
4. **Validador** — `sqlglot` parsea `MATCH ... AGAINST ... IN BOOLEAN MODE` nativamente y `MATCH`/`AGAINST` no están en la blocklist. Cero cambios en `sql_validator.py`. La triple defensa anti-injection se preserva intacta.

### Resultados (smoke test post-cambio)

| Query usuario | SQL emitido | Filas |
|---|---|---|
| "APARTAMENTO SAN ISIDRO 2021" | solo MATCH | 1 ✓ |
| "Busco casas de 3 habitaciones en zona 10" | `tipo='casa' AND habitaciones=3 AND MATCH('+"zona 10"')` | 2 ✓ |
| "Muéstrame departamentos de menos de $150,000" | solo structured, **sin MATCH** | 4 ✓ |
| ">2 baños y al menos 150 m²" | solo structured, **sin MATCH** | 5 ✓ |
| "Terrenos entre $50K y $100K" | solo structured, **sin MATCH** | 3 ✓ |
| "Departamentos con 2 hab en zona 15" | `tipo='departamento' AND habitaciones=2 AND MATCH('+"zona 15"')` | 2 ✓ |

El LLM discrimina correctamente: emite MATCH solo cuando hay texto libre real, y los 6 ejemplos canónicos del assessment (PDF) siguen resolviendo.

### Tradeoffs y límites conocidos

- **`innodb_ft_min_token_size = 3`** (default): tokens de 1-2 caracteres se ignoran. No afecta los queries esperados.
- **Stopwords default** son inglesas; no chocan con vocabulario inmobiliario en español.
- **Sin stemming nativo**: `"apartamento"` no matchea `"departamento"` por similitud léxica. Resuelto vía el mapeo de sinónimos del prompt + el hecho de que las filas reales suelen incluir la palabra del usuario en `titulo` o `descripcion`.
- **Extensión futura**: si aparecen typos o variantes morfológicas frecuentes, cambiar el índice a `WITH PARSER ngram` permite matching sub-token (más recall, más falsos positivos).

---

## 🧪 Tests

```bash
pytest                                  # 138 tests
pytest --cov=app                        # cobertura 96% global, 97% sql_validator
ruff check app/                         # lint
mypy app/ persistencia/                 # types
lizard app/ persistencia/ --CCN 10 -L 30 # complexity
```

| Test layer | Files | Count |
|---|---|---|
| Unit | `tests/unit/test_*.py` (7 archivos) | 96 |
| Integration | `tests/integration/test_*.py` (3 archivos) | 25 |
| Contract | `tests/contract/test_*.py` (3 archivos) | 17 |
| **Total** | | **138** |

---

## 🔧 Variables de entorno

Definidas en `proyecto-propiedades/.env.example` (root). El compose root inyecta los valores al container.

| Variable | Default | Descripción |
|---|---|---|
| `MYSQL_USER` | `appuser` | User MySQL (también `DB_USER` interno) |
| `MYSQL_PASSWORD` | `apppass` | Password |
| `MYSQL_DATABASE` | `propiedades_db` | DB name |
| `LLM_BACKEND` | `ollama` | `ollama` \| `mock` |
| `OLLAMA_URL` | `http://host.docker.internal:11434` | URL del runtime |
| `OLLAMA_MODEL` | `llama3.2:3b` | Modelo |
| `OLLAMA_TIMEOUT_SECONDS` | `15` | Timeout duro |
| `MOCK_LLM` | `false` | Rollback a SQL canned |
| `LOG_LEVEL` | `INFO` | DEBUG/INFO/WARNING/ERROR |
| `CORS_ORIGINS` | `["http://localhost:8080","http://localhost:5173"]` | Allow-list |

---

## 🗄 Migraciones idempotentes

Defensa en 3 capas:

1. **`/docker-entrypoint-initdb.d`** — Docker `mysql:8.0` corre `persistencia/01_schema.sql` + `02_seed_data.sql` en primer arranque
2. **SQL idempotente** — `CREATE TABLE IF NOT EXISTS` + `INSERT IGNORE` con UNIQUE constraint
3. **`run_migrations_if_needed()` Python** — invocado desde lifespan, valida `table_exists` y `count >= MIN_SEED_ROWS`

---

## 🩺 Troubleshooting

| Síntoma | Causa | Fix |
|---|---|---|
| `OperationalError 2003` | MySQL no listo | Usar override (`condition: service_healthy`) |
| `httpx.ConnectError 11434` | Ollama no responde | `ollama serve` en el host |
| `LLM_TIMEOUT` recurrente | Modelo lento | Aumentar `OLLAMA_TIMEOUT_SECONDS` |
| Linux: `host.docker.internal` no resuelve | OS sin DNS Docker | Override añade `extra_hosts: host-gateway` |

## 📄 License

MIT
