# proyecto-propiedades · Frontend

> **SPA Vue 3.5** — Composition API + TypeScript + Vite + Pinia + Tailwind CSS 3

UI para `POST /api/search`: input en lenguaje natural, grid de resultados con cards responsive, estados loading/error/empty, toggle "Mostrar SQL generado".

[![Vue](https://img.shields.io/badge/Vue-3.5-42b883.svg)](https://vuejs.org)
[![TypeScript](https://img.shields.io/badge/TS-5.7-3178c6.svg)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-5.4-646cff.svg)](https://vitejs.dev)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen.svg)]()

---

## 🚀 Levantar la app

El orquestador vive en el root del proyecto (`proyecto-propiedades/`). Ver el [README root](../README.md).

```bash
cd ..
cp .env.example .env
docker compose up -d --build       # mysql + backend + frontend (este)
open http://localhost:8080
```

## 🛠 Dev nativo (Vite HMR)

```bash
# Necesita backend corriendo en :8000 (vía compose root)
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev                        # http://localhost:5173
```

---

## 📜 Scripts

| Comando | Descripción |
|---|---|
| `npm run dev` | Vite dev server con HMR en `:5173` |
| `npm run build` | Producción → `dist/` (151kB / 58.8kB gzip) |
| `npm run preview` | Sirve `dist/` localmente en `:4173` |
| `npm run test` | vitest watch |
| `npm run test:ci` | vitest run + cobertura |
| `npm run typecheck` | `vue-tsc --noEmit` |
| `npm run gen:types` | Regenera `src/types/api.ts` desde el OpenAPI |

## 🔧 Variables

El compose root pasa `VITE_API_BASE_URL` como build arg. Para dev nativo se usa `.env.local`:

```
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🏗 Estructura

```
src/
├── App.vue                  # Shell con RouterView + AppHeader
├── main.ts                  # Bootstrap Vue + Pinia + Router
├── router/index.ts          # 1 ruta: / → SearchView
├── views/SearchView.vue     # Vista única
├── components/              # Atomic Design
│   ├── SearchBar.vue
│   ├── PropertyCard.vue
│   ├── PropertyGrid.vue
│   ├── EmptyState.vue
│   ├── ErrorAlert.vue
│   ├── LoadingSpinner.vue
│   ├── SqlPreview.vue
│   └── AppHeader.vue
├── composables/useSearch.ts # Wrapper del store
├── stores/search.ts         # Pinia store
├── services/api.ts          # axios client con ApiError envelope
├── types/api.ts             # Tipos espejo del OpenAPI
└── assets/main.css
```

### Patrones aplicados

- **Composable** — `useSearch` reusable en cualquier componente
- **Pinia store** — estado reactivo centralizado
- **Single axios surface** — `services/api.ts`
- **Atomic Design** — cada componente < 150 LOC, una responsabilidad
- **Error envelope mapping** — `ApiError` con `code` humanizado (10 mappings)

---

## 🎨 UI Kit

Paleta Tailwind extendida (`tailwind.config.ts`):
- **primary** (azul confianza 50–950): `#1183ed`, `#0866cb`, `#0e3a6e`
- **accent** (terracota cálido 50–900): `#dd5832`, `#cc4324`
- **neutral** (9 escalones)

Typography: **Inter** sans + **JetBrains Mono** (para SQL preview).
Component utilities: `.btn-primary`, `.btn-secondary`, `.input-search`, `.chip`, `.card`.

---

## 🧪 Tests (vitest + happy-dom)

```bash
npm run test:ci
```

| Archivo | Tests |
|---|---|
| `tests/unit/useSearch.spec.ts` | 7 |
| `tests/unit/SearchView.spec.ts` | 7 |
| `tests/unit/api.spec.ts` | 6 |
| **Total** | **20** |

Cobertura: **91.6% global**.

---

## 🩺 Troubleshooting

| Síntoma | Fix |
|---|---|
| CORS error en consola | Backend debe incluir el origin en `CORS_ORIGINS` |
| `Network error` axios | Verificar `VITE_API_BASE_URL` y backend arriba |
| HMR no actualiza en Docker | `vite.config.ts` con `server.watch.usePolling=true` |
| Build emite `.js` shadows | Asegurar `noEmit: true` en `tsconfig.json` |

## 📄 License

MIT
