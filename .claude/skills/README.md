# Skills · proyecto-propiedades

Skills (knowledge packs) importados desde el repo padre `.claude/skills/`, filtrados y adaptados al stack de este proyecto:

- **Frontend:** Vue 3.5 + Composition API + Tailwind 3 + Vite
- **Backend:** FastAPI 0.115 (Python 3.12)
- **BD:** MySQL 8
- **LLM:** Ollama `llama3.2:3b`
- **Docs site:** Docusaurus 3.8 + `@scalar/docusaurus`

## Skills aplicables (importados)

| Skill | Para qué | Targets concretos |
|---|---|---|
| `a11y-check` | Auditar WCAG 2.1 AA | `frontend/dist/index.html`, `backend-developer/build/**/*.html`, `static/diagrams/*.html` |
| `design-patterns` | Audit de patrones GoF + idioms Python/TS | `backend/app/` (ya cubre Repository/Adapter/Strategy/Factory) |
| `html-validate` | W3C compliance | Misma cobertura que a11y-check |
| `perf-audit` | LCP, CLS, Core Web Vitals | `frontend/dist/`, `backend-developer/build/` |
| `seo-check` | Meta tags, JSON-LD, Open Graph | `backend-developer/build/` (no aplica al backend FastAPI ni al SPA Vue) |
| `ui-ux-pro-max` | Audit visual + design tokens | `frontend/src/components/` + `tailwind.config.ts` |
| `web-design-guidelines` | Best practices web genéricas | `frontend/src/` + componentes |

## Skills NO aplicables (no se importaron)

| Skill | Razón |
|---|---|
| `next-best-practices` | No usamos Next.js (el frontend es Vue) |
| `vercel-react-best-practices` | Aplica a React/Next; nuestro frontend es Vue |
| `pencil-design` | No usamos `.pen` files |
| `remotion-best-practices` | No usamos Remotion (video React) |
| `design-review` | Mide contra el design system "1Platform"; nuestro UI Kit es independiente |

## Cómo invocar

Los skills se cargan automáticamente cuando el contexto del prompt coincide con su `description`. Para forzar uno explícitamente, mencionarlo:

> "Aplica `a11y-check` sobre el build del frontend"
> "Audita `design-patterns` en `backend/app/`"

## Aplicaciones que dejaron rastro en `CHANGELOG.md`

- `code-review` ya cubrió `design-patterns` (verificación grep DIP/Repository/Adapter)
- Aplicaciones manuales recientes se anotan en `CHANGELOG.md` con fecha + hallazgos
