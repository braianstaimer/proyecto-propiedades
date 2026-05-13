# proyecto-propiedades · API Documentation Site (Bonus)

> Docusaurus 3.8 + `@scalar/docusaurus` plugin para servir el OpenAPI 3.1 spec del backend como referencia interactiva.

[![Docusaurus](https://img.shields.io/badge/Docusaurus-3.8-25c2a0.svg)](https://docusaurus.io)
[![Scalar](https://img.shields.io/badge/Scalar-API_Reference-e7472c.svg)](https://scalar.com)

> **Bonus** — fuera del compose root (`proyecto-propiedades/docker-compose.yml`). Se corre por separado con `npm`.

---

## 🚀 Quickstart

```bash
npm install
npm start                         # http://localhost:3001 (dev)
```

## 🏗 Build estático

```bash
npm run build                     # → build/
npm run serve                     # sirve build/ en :3001
```

## 🔄 Sincronizar spec desde el backend

```bash
# 1. Backend debe estar arriba (compose root):
curl http://localhost:8000/api/health

# 2. Refrescar spec
OPENAPI_URL=http://localhost:8000/openapi.json node scripts/fetch-openapi.mjs

# 3. Rebuild
npm run build
```

---

## 📖 Estructura

```
backend-developer/
├── docusaurus.config.ts      # Docusaurus 3.8.1 (3.9 incompatible con webpack 5.106)
├── sidebars.ts
├── package.json              # overrides.webpack=5.99.6 (workaround)
├── scripts/
│   └── fetch-openapi.mjs     # Hidrata static/openapi.json desde OPENAPI_URL
├── src/css/custom.css        # Paleta coherente con el frontend Vue
├── static/
│   ├── openapi.json          # Spec OpenAPI 3.1 versionado
│   └── img/favicon.svg
└── docs/
    ├── intro.md              # Quickstart + curl examples
    ├── flows/search-flow.md  # Sequence diagram del pipeline NL→SQL
    ├── architecture/error-codes.md
    └── reference/health.md
```

---

## 🧩 Plugin Scalar

`@scalar/docusaurus@0.5.4` monta la spec en `/api-reference/`. La spec se carga client-side desde `static/openapi.json` (offline-safe).

---

## 🔧 Decisiones técnicas

### Docusaurus 3.8.1 (no 3.9.0)

Docusaurus 3.9 falla con `ValidationError: Invalid options object. Progress Plugin` cuando webpack 5.106 está hoisted. Workaround:
- Pin `@docusaurus/core` a `3.8.1`
- `overrides.webpack: "5.99.6"` en `package.json`

### Spec consumida client-side

Para evitar build-time fetches (que rompen offline), el spec vive en `static/openapi.json` y Scalar lo carga con `<script>` en runtime.

---

## 📜 Scripts

| Comando | Descripción |
|---|---|
| `npm start` | Docusaurus dev server :3001 |
| `npm run build` | Build estático en `build/` |
| `npm run serve` | Sirve `build/` en :3001 |
| `npm run fetch-openapi` | Refresca `static/openapi.json` |
| `npm run clear` | Limpia cache |

## 🌐 Páginas

| Ruta | Contenido |
|---|---|
| `/intro` | Quickstart + curl examples + 6 búsquedas demo |
| `/flows/search-flow` | Sequence diagram del pipeline NL→SQL |
| `/architecture/error-codes` | Catálogo de 13 códigos |
| `/reference/health` | Documentación de `GET /api/health` |
| `/api-reference` | Scalar UI interactiva sobre el OpenAPI 3.1 |

## 📄 License

MIT
