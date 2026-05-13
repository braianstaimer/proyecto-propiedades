---
description: Audita y mejora la suite de tests de backend. Apunta a cobertura ≥70% con foco en rutas críticas (validador SQL, endpoint de search, integración LLM mockeado).
allowed-tools: Bash, Read, Edit, Write, Grep, Glob
---

# /test-audit · proyecto-propiedades

Audita la suite de tests del backend (`backend/tests/`) y la lleva a cobertura mínima viable con énfasis en rutas críticas (security: SQL injection, LLM contracts).

> **Alcance reducido vs monorepo:** una sola feature (search). Pyramid mínima: muchos unit (validador, prompt builder, mappers), pocos integration (endpoint con LLM mockeado + MySQL real), 0 E2E (out of scope).

---

## Misión

Garantizar que:

1. Cobertura global del backend ≥ **70%** (rule del PDF: tests no obligatorios pero valorados).
2. Cobertura de `app/sql_validator.py` ≥ **95%** (componente de seguridad).
3. Cobertura de `app/llm_service.py` ≥ **80%** (con mock httpx).
4. Cobertura del endpoint `POST /api/search` ≥ **85%** (todos los códigos de error tipados).
5. Tests son **deterministas** (sin red real, sin tiempo real, sin LLM real).
6. Estructura clara: `tests/unit/`, `tests/integration/`, `tests/contract/`.

---

## Layout objetivo

```
backend/tests/
├── conftest.py                        # fixtures globales: db_session, mock_llm, client
├── unit/
│   ├── test_sql_validator.py          # ★ crítico: 30+ casos adversariales
│   ├── test_prompt_builder.py         # prompt v1 incluye few-shot, schema, reglas
│   ├── test_property_repository.py    # mappers ORM → schema
│   └── test_search_service.py         # orquestación con LLM/repo mockeados
├── integration/
│   ├── test_search_endpoint.py        # POST /api/search end-to-end con LLM mockeado y MySQL real
│   ├── test_health_endpoint.py        # GET /api/health con DB real, LLM mockeado
│   └── test_db_schema.py              # SHOW CREATE TABLE valida estructura
└── contract/
    └── test_openapi_snapshot.py       # snapshot del openapi.json estable
```

---

## Procedimiento (autónomo)

### Paso 1 — Baseline
```bash
cd backend
source venv/bin/activate
pytest --cov=app --cov-report=term-missing --cov-report=json:/tmp/cov_before.json
COV_BEFORE=$(python -c "import json;print(json.load(open('/tmp/cov_before.json'))['totals']['percent_covered'])")
echo "Baseline coverage: ${COV_BEFORE}%"
```

### Paso 2 — Inventario de gaps
```bash
pytest --cov=app --cov-report=term-missing 2>&1 | grep "TOTAL\|Missing"
```
Identificar archivos con cobertura < target.

### Paso 3 — Casos adversariales obligatorios para `test_sql_validator.py`

Cada caso es un test parametrizado:

```python
INVALID_SQL_CASES = [
    # Estructura
    ("DROP TABLE propiedades", "SQL_NOT_SELECT"),
    ("DELETE FROM propiedades WHERE 1=1", "SQL_NOT_SELECT"),
    ("UPDATE propiedades SET precio=0", "SQL_NOT_SELECT"),
    ("INSERT INTO propiedades VALUES (...)", "SQL_NOT_SELECT"),
    ("TRUNCATE propiedades", "SQL_NOT_SELECT"),
    ("ALTER TABLE propiedades ADD COLUMN x INT", "SQL_NOT_SELECT"),
    ("CREATE TABLE x (...)", "SQL_NOT_SELECT"),
    # Multi-statement
    ("SELECT 1; DROP TABLE propiedades", "SQL_NOT_SELECT"),
    # Tabla prohibida
    ("SELECT * FROM users", "SQL_FORBIDDEN_TABLE"),
    ("SELECT * FROM information_schema.tables", "SQL_FORBIDDEN_TABLE"),
    ("SELECT * FROM mysql.user", "SQL_FORBIDDEN_TABLE"),
    # Funciones peligrosas
    ("SELECT SLEEP(60) FROM propiedades", "SQL_DANGEROUS_FUNCTION"),
    ("SELECT BENCHMARK(1000000, MD5('a')) FROM propiedades", "SQL_DANGEROUS_FUNCTION"),
    ("SELECT LOAD_FILE('/etc/passwd') FROM propiedades", "SQL_DANGEROUS_FUNCTION"),
    ("SELECT * FROM propiedades INTO OUTFILE '/tmp/x'", "SQL_DANGEROUS_FUNCTION"),
    # Ruido del LLM
    ("```sql\nSELECT * FROM propiedades\n```", "VALID"),  # tras post-procesado
    ("Aquí tienes:\nSELECT * FROM propiedades;", "LLM_INVALID_OUTPUT"),
    # Vacío / inválido
    ("", "LLM_INVALID_OUTPUT"),
    ("SELECT", "LLM_INVALID_OUTPUT"),
    ("not sql at all", "LLM_INVALID_OUTPUT"),
    # Subquery a tabla prohibida
    ("SELECT * FROM propiedades WHERE id IN (SELECT user_id FROM users)", "SQL_FORBIDDEN_TABLE"),
    # Comentarios sospechosos
    ("SELECT * FROM propiedades -- AND 1=1", "VALID"),  # comentarios SQL son legales en SELECT puro
    ("SELECT * /*! DROP TABLE x */ FROM propiedades", "SQL_NOT_SELECT"),  # MySQL hint comments
]
```

### Paso 4 — Mock del LLM

`tests/conftest.py` debe exponer:
```python
@pytest.fixture
def mock_llm(monkeypatch):
    """Mockea LLMService.generate_sql para devolver el SQL deseado."""
    from app.services import llm_service
    async def fake_generate_sql(query: str) -> str:
        return MOCK_LLM_RESPONSES.get(query, "SELECT * FROM propiedades LIMIT 1")
    monkeypatch.setattr(llm_service.LLMService, "generate_sql", fake_generate_sql)
```

### Paso 5 — Tests del endpoint con MySQL real

Usar **testcontainers-python** O fallback a **MySQL del compose** ya corriendo:

```python
@pytest.fixture(scope="session")
async def db_session():
    # Conecta a la DB del docker-compose si está disponible,
    # sino usa testcontainers para spinear MySQL efímero.
    ...
```

### Paso 6 — Iteración

```bash
pytest --cov=app --cov-report=term-missing --cov-report=json:/tmp/cov_after.json
COV_AFTER=$(python -c "import json;print(json.load(open('/tmp/cov_after.json'))['totals']['percent_covered'])")
echo "After: ${COV_AFTER}% (was ${COV_BEFORE}%)"
```

Repetir Pasos 3–6 hasta:
- Cobertura global ≥ 70%
- `sql_validator` ≥ 95%
- 0 tests `xfail`/`skip` sin justificación documentada

### Paso 7 — Calidad de los tests

```bash
# No tests vacíos
grep -rn "def test_" tests/ | xargs -I{} grep -L "assert" {} || true

# Cada test tiene un assert
pytest --collect-only -q | wc -l   # # tests
grep -rn "assert" tests/ | wc -l    # # asserts (debería ser ≥ # tests)

# Sin fixtures sin uso
pytest --setup-show 2>&1 | grep "fixture" | sort -u
```

### Paso 8 — Documentar
- Actualizar `assessments/CHANGELOG.md`: `Tests · audit pass <fecha>` con `before → after %`.
- Si cobertura < target tras 2 iteraciones, abrir entrada `Risk · cobertura sub-target`.

---

## Anti-patrones a evitar (rule heredada)

- ❌ Tests que mockean Pydantic con `MagicMock(spec=...)` y luego rompen al añadir campos. Usar instancias reales.
- ❌ Tests que dependen del orden de ejecución (`pytest-order`).
- ❌ `time.sleep` en tests; usar `freezegun` o time-travel fixtures.
- ❌ Llamadas reales a Ollama o MySQL en suite unit.
- ❌ Suprimir warnings sin causa documentada.

---

## Checklist final

- [ ] `pytest --cov=app` reporta ≥ 70% global, ≥ 95% en validator
- [ ] 30+ tests parametrizados en `test_sql_validator.py`
- [ ] Endpoint `/api/search` cubre los 7 códigos de error del catálogo
- [ ] No hay tests `skip`/`xfail` sin comentario explicativo
- [ ] CI workflow `.github/workflows/ci.yml` corre `pytest --cov` y publica resumen
- [ ] CHANGELOG actualizado
