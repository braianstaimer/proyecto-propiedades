---
description: Verifica que el contrato OpenAPI del backend backend esté en sync con (a) los tipos consumidos por el frontend Vue y (b) la copia versionada en backend-developer.
allowed-tools: Bash, Read, Edit, Write, Grep, Glob
---

# /contract-check · proyecto-propiedades

Garantiza coherencia three-way:

```
       ┌──────────────────────────────────────────────────────┐
       │                                                       │
       │  backend/app/main.openapi()                       │
       │            │                                          │
       │            ├──→  frontend/src/types/api.ts    │
       │            │     (generado por openapi-typescript)    │
       │            │                                          │
       │            └──→  backend-developer/static/openapi.json
       │                  (servido por Scalar)                 │
       │                                                       │
       └──────────────────────────────────────────────────────┘
```

Si los tres puntos no concuerdan, hay deriva de contrato → bug latente en runtime.

> **Diferencia con `/audit-openapi`:** ese es ofensivo (mejorar la spec). Este es defensivo (no romper consumidores).

---

## Misión

1. Re-exportar la spec viva del backend.
2. Diff vs la copia en `backend-developer/static/openapi.json` → si difiere, sincronizar y commit.
3. Re-generar `frontend/src/types/api.ts` y type-check.
4. Verificar que los `axios` calls del front usan paths reales del backend (`/api/search`, `/api/health`) — no hay 404s latentes.
5. Actualizar `assessments/CHANGELOG.md`.

---

## Procedimiento

### Paso 1 — Spec actual del backend
```bash
cd backend
source venv/bin/activate
python -c "import json,importlib; m=importlib.import_module('app.main'); print(json.dumps(m.app.openapi(), indent=2, sort_keys=True))" \
  > /tmp/openapi_live.json
```

### Paso 2 — Comparar con el spec versionado en docs

```bash
DOCS_SPEC=../backend-developer/static/openapi.json
diff <(jq -S . "$DOCS_SPEC") <(jq -S . /tmp/openapi_live.json) > /tmp/spec_diff.txt
DIFF_LINES=$(wc -l < /tmp/spec_diff.txt)

if [ "$DIFF_LINES" -gt 0 ]; then
  echo "❌ Contract drift: $DIFF_LINES líneas de diff"
  head -80 /tmp/spec_diff.txt
  echo ""
  echo "Sincronizando..."
  cp /tmp/openapi_live.json "$DOCS_SPEC"
  echo "✅ Spec en docs actualizada. Commit recomendado."
else
  echo "✅ Spec en docs en sync"
fi
```

### Paso 3 — Regenerar tipos TypeScript del frontend

```bash
cd ../frontend
# devDep: openapi-typescript
npx openapi-typescript /tmp/openapi_live.json -o src/types/api.ts
git diff --stat src/types/api.ts
```

Validar que los tipos generados se usan:
```bash
grep -rn "from '@/types/api'" src/ || echo "⚠️  Nadie importa los tipos generados"
```

### Paso 4 — Type-check del frontend
```bash
npm run typecheck
# vue-tsc --noEmit; debe terminar sin errores
```

### Paso 5 — Cazar paths hard-coded inconsistentes

```bash
# Paths que el frontend efectivamente llama:
grep -rn "axios\|api\.\|fetch(" src/ | grep -oE "/api/[a-z/]*" | sort -u > /tmp/front_paths.txt

# Paths que el backend expone:
jq -r '.paths | keys[]' /tmp/openapi_live.json | sort -u > /tmp/api_paths.txt

# Diff: paths que el front llama pero el backend no tiene
comm -23 /tmp/front_paths.txt /tmp/api_paths.txt
# Expected: empty

# Paths que el backend tiene pero nadie llama (informativo)
comm -13 /tmp/front_paths.txt /tmp/api_paths.txt
```

### Paso 6 — Validar shapes de request/response

Los tipos TS generados deben coincidir con lo que el front envía. Test rápido:

```bash
cd ../frontend
# Asegurar que SearchRequest del backend (Pydantic) tenga el mismo shape
# que lo que envía el composable useSearch.
grep -rn "interface SearchRequest\|type SearchRequest" src/types/api.ts
grep -rn "{ query:" src/composables/useSearch.ts
```

### Paso 7 — Ejecutar smoke contract con backend vivo

```bash
# Asume backend en :8000
curl -s -X POST http://localhost:8000/api/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"smoke"}' | jq -e '.query and .sql and (.results|type=="array") and (.count|type=="number") and (.took_ms|type=="number")'
```

Si jq falla (algún campo ausente), el contrato se rompió en runtime aunque la spec compile.

### Paso 8 — Commit + CHANGELOG
```bash
# Si hubo drift
git -C ../backend-developer add static/openapi.json
git -C ../backend-developer commit -m "docs(openapi): sync spec from backend"

git -C ../frontend add src/types/api.ts
git -C ../frontend commit -m "chore(types): regen api.ts from openapi"
```

Anotar en `assessments/CHANGELOG.md`:
```
### YYYY-MM-DD — Contract sync
- Drift detectado: X líneas
- Tipos regenerados: src/types/api.ts (+/− N)
- Smoke E2E: ✓
```

---

## Modos de falla y qué hacer

| Falla | Causa típica | Fix |
|---|---|---|
| `comm -23` no vacío | Front llama a un path que el backend no tiene | Renombrar el call del front o agregar el endpoint |
| typecheck falla en `src/types/api.ts` | Cambio breaking en el schema (rename/remove) | Actualizar el composable/store consumer |
| Smoke devuelve `422 LLM_TIMEOUT` aleatorio | Ollama lento — no es contract drift | No bloqueante; documentar |
| `jq -e` falla por campo ausente | El backend "olvidó" un campo en `SearchResponse` | Re-añadir, agregar test contract |

---

## Checklist final

- [ ] `static/openapi.json` en docs == `app.openapi()` viva
- [ ] `src/types/api.ts` regenerado y commiteado
- [ ] `npm run typecheck` verde
- [ ] `comm -23 front_paths api_paths` vacío
- [ ] Smoke contract `curl` con `jq -e` pasa
- [ ] CHANGELOG actualizado
