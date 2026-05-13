---
description: Code-review pre-merge autónomo para proyecto-propiedades. Audita backend (FastAPI), frontend (Vue 3) y bonus docs. Detecta dead code, anti-patterns, drift de contrato y regresiones de coverage.
allowed-tools: Bash, Read, Edit, Write, Grep, Glob
---

# /code-review · proyecto-propiedades

Audit pre-merge del repo. Adaptado a este stack: FastAPI plano + Vue 3 Composition API + MySQL + Ollama. Iterativo: encuentra issues, reporta severidad, aplica fixes seguros, vuelve a correr verificaciones hasta APROBADO.

> **Diferencia con `/audit-openapi` y `/contract-check`:** ese audit es ofensivo (mejorar spec) y el check es defensivo (no romper consumidores). Este review es **integral**: dead code + anti-patterns + tests + métricas.

---

## Misión

Garantizar que el código que se va a mergear:

1. **No tiene código muerto** — imports sin usar, helpers sin caller, branches inalcanzables, archivos huérfanos.
2. **Respeta los patrones de `PATTERNS.md`** — verificables por grep (DIP, Repository, Adapter, DTO, etc.).
3. **No viola anti-patterns prohibidos** (PLAN.md §20).
4. **Pasa las gates** — ruff/mypy/lizard/pytest backend; vitest/vue-tsc frontend.
5. **Mantiene cobertura** ≥80% backend, ≥95% en `sql_validator`.
6. **OpenAPI y tipos TS están sincronizados** (delegar en `/contract-check`).
7. **Documentación viva** — READMEs reflejan la estructura real.

---

## Procedimiento autónomo (iterativo)

### Iteración 1 — Inventario y anti-patterns

```bash
# 1.1 Estado del repo
git status --short
git log --oneline -10

# 1.2 Dead code · imports no usados, helpers sin caller (backend)
cd backend
source venv/bin/activate
ruff check app/ persistencia/ --select F401,F811,F841,B007 --statistics

# 1.3 Dead code · vars/funciones declarados pero no usados
ruff check app/ persistencia/ --select ARG001,ARG002,ERA001 || true

# 1.4 Branches inalcanzables (heurística)
grep -rnE "if False:|if 0:|return.*\n\s+return" app/ || true

# 1.5 Comentarios TODO/FIXME huérfanos
grep -rnE "TODO|FIXME|XXX|HACK" app/ persistencia/ tests/ || true
grep -rnE "TODO|FIXME|XXX|HACK" ../frontend/src/ ../frontend/tests/ || true

# 1.6 Archivos huérfanos (sin importadores)
for f in app/*.py; do
  base=$(basename "$f" .py)
  [ "$base" = "__init__" ] && continue
  [ "$base" = "main" ] && continue
  count=$(grep -rE "from app.${base}|import app.${base}|app/${base}.py" app/ tests/ 2>/dev/null | wc -l)
  [ "$count" -eq 0 ] && echo "⚠ ORPHAN: $f"
done
```

### Iteración 2 — Patrones (grep auditable de PATTERNS.md)

```bash
# 2.1 DIP — SearchService no importa infraestructura
grep -E "import (httpx|aiomysql|sqlalchemy|mysql|ollama|requests)" backend/app/search_service.py
# expected: vacío

# 2.2 Repository — única superficie SQL
grep -rnE "text\(|\.execute\(|cursor" backend/app/ \
  | grep -v "repositories.py\|database.py\|tests/\|persistencia/runner.py"
# expected: vacío

# 2.3 Adapter — LLM HTTP sólo en llm_service.py
grep -rn "httpx\|Ollama" backend/app/ | grep -v "llm_service.py\|tests/\|conftest"
# expected: vacío

# 2.4 Layered — routes.py no importa SQLAlchemy ni httpx
grep -E "import (sqlalchemy|aiomysql|httpx)" backend/app/routes.py
# expected: vacío

# 2.5 lru_cache sólo en get_settings
grep -B1 "lru_cache" backend/app/*.py | grep -v "get_settings"
# expected: vacío

# 2.6 Frontend — axios sólo en services/api.ts
grep -rn "axios.post\|axios.get\|fetch(" frontend/src/ | grep -v "services/api.ts"
# expected: vacío

# 2.7 Frontend — VITE_API_BASE_URL nunca hardcoded
grep -rn "localhost:8000" frontend/src/ | grep -v ".test.\|.spec."
# expected: vacío (usa import.meta.env.VITE_API_BASE_URL)

# 2.8 Frontend — v-html sólo si justificado
grep -rn 'v-html' frontend/src/
# expected: vacío o con sanitización explícita
```

### Iteración 3 — Anti-patterns prohibidos (PLAN.md §20)

```bash
# 3.1 String concat para SQL
grep -rnE "f\".*SELECT|f\".*FROM|f\".*WHERE|\\+.*SELECT|\\+.*FROM" backend/app/ \
  | grep -v "test_\|prompts.py\|repositories.py.*PropertyRow"
# expected: vacío

# 3.2 eval/exec/pickle/subprocess
grep -rnE "\beval\(|\bexec\(|pickle\.loads|subprocess" backend/app/ frontend/src/
# expected: vacío

# 3.3 time.sleep en código async
grep -rn "time.sleep" backend/app/
# expected: vacío (usar asyncio.sleep)

# 3.4 Captura genérica de Exception
grep -rn "except Exception:" backend/app/ | grep -v "test_\|conftest"
# expected: si aparece, debe re-raisear tipado

# 3.5 Modelo hardcoded
grep -rn "llama3" backend/app/ | grep -v "prompts.py\|config.py.*default"
# expected: vacío

# 3.6 LIMIT > 200 sin clamp
grep -rnE "LIMIT [2-9][0-9]{2}|LIMIT [0-9]{4,}" backend/app/ | grep -v "test_\|validator"
# expected: vacío
```

### Iteración 4 — Tests + cobertura

```bash
# Backend
cd backend
pytest --cov=app --cov-report=term-missing --cov-fail-under=80 -q

# Cobertura crítica
pytest --cov=app.sql_validator --cov-fail-under=95 tests/unit/test_sql_validator.py -q

# Smoke específico (si existe)
pytest tests/smoke/ -v 2>/dev/null || echo "no smoke tests yet"

# Frontend
cd ../frontend
npm run test:ci -- --reporter=verbose 2>&1 | tail -20
npm run typecheck
```

### Iteración 5 — Gates de quality

```bash
# Backend
cd backend
ruff check app/ persistencia/ tests/
mypy app/ persistencia/
lizard app/ persistencia/ --CCN 10 -L 30

# Frontend
cd ../frontend
npm run typecheck
npm run build
```

### Iteración 6 — Docs y contrato

```bash
# OpenAPI snapshot
cd backend
pytest tests/contract/test_openapi_snapshot.py -v

# Spec live vs docs
diff <(python -c "import json; from app.main import app; print(json.dumps(app.openapi(), sort_keys=True, indent=2))") \
     <(python -c "import json,sys; print(json.dumps(json.load(open('../backend-developer/static/openapi.json')), sort_keys=True, indent=2))")
# expected: vacío

# Estructura PDF preservada
test -f backend/app/__init__.py && \
test -f backend/app/main.py && \
test -f backend/app/models.py && \
test -f backend/app/routes.py && \
test -f backend/app/llm_service.py && \
echo "✓ PDF layout intact"
```

---

## Severidad y triage

| Severidad | Bloquea merge | Ejemplos |
|---|---|---|
| 🔴 CRITICAL | sí | DIP violado, SQL concat, eval, dead branch en validator |
| 🟠 HIGH | sí | Coverage < 80%, anti-pattern PATTERNS.md, except Exception sin re-raise |
| 🟡 MEDIUM | preferible fix | Import sin usar, helper sin caller, TODO sin fecha |
| 🟢 LOW | nice to have | Comentario obsoleto, naming subóptimo no crítico |

---

## Reporte final

```markdown
## Code Review · proyecto-propiedades · YYYY-MM-DD

**Veredicto:** APROBADO | REQUIERE CAMBIOS | RECHAZADO

### Iteración N
- 🔴 0 critical
- 🟠 0 high
- 🟡 N medium (lista)
- 🟢 N low (lista)

### Métricas
- Backend coverage global: NN.NN% (target ≥80%) ✓
- Backend coverage sql_validator: NN.NN% (target ≥95%) ✓
- Frontend coverage: NN.NN%
- ruff/mypy/lizard/vue-tsc: PASS
- pytest: N tests, 0 fail
- vitest: N tests, 0 fail

### Grep patterns
- DIP search_service.py: vacío ✓
- Repository única superficie SQL: vacío ✓
- Adapter Ollama: vacío ✓
- Frontend axios: vacío ✓

### Fixes aplicados esta iteración
- (lista de archivos modificados con motivo)

### Pendiente
- (nada o lista corta)
```

---

## Loop de iteración

1. Correr iteraciones 1–6.
2. Si hay 🔴 o 🟠: aplicar fixes en lote (sin scope creep).
3. Volver a 1.
4. Repetir hasta `0 critical + 0 high`.
5. Reportar APROBADO en `CHANGELOG.md`.

Si tras 3 iteraciones sigue habiendo 🔴, REPORTAR y pedir guía al humano.
