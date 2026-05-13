# Prompt para Claude Code

> Copia y pega esto en Claude Code al abrir el repo `proyecto-propiedades` (estando posicionado en `frontend/`).

---

Tengo un rediseño del frontend en este paquete (`design_handoff_uikit_redesign/`). Es un rediseño **editorial high-fidelity** del SPA actual — misma funcionalidad, mejor presentación. Los archivos de referencia están en `reference/` (prototipos React); **no los copies**, son sólo visualización.

**Stack objetivo (no cambiar):** Vue 3.5 Composition API + TS + Tailwind 3 + Pinia + axios. Los tokens ya están en `frontend/tailwind.config.ts`.

**Antes de tocar nada:**

1. Lee `design_handoff_uikit_redesign/README.md` completo. Es la fuente de verdad — tiene specs por componente, copy exacto, layout, tokens y checklist final.
2. Abre `design_handoff_uikit_redesign/reference/index.html` en un navegador para ver el target visual.
3. Lee los componentes Vue actuales en `frontend/src/components/` y `frontend/src/views/SearchView.vue` para entender la base.
4. Lee `frontend/src/assets/main.css` y `frontend/tailwind.config.ts` para conocer las utilities/tokens disponibles.

**Plan de implementación (sigue este orden):**

1. **Crea los 3 componentes nuevos** (`Eyebrow.vue`, `SuggestionChips.vue`, `ResultBar.vue`) en `frontend/src/components/`. Specs exactos en el README.
2. **Reestructura `SearchView.vue`** en dos bandas (hero-band + main). Incorpora los 3 nuevos componentes. Wire `SuggestionChips @pick` a `inputValue = s; search(s)`. Wire `ResultBar @reset` a `store.reset(); inputValue = ''`.
3. **Actualiza `PropertyCard.vue`** — badge de tipo absoluto en el gradient, quita el chip de tipo del body, añade hover lift (clase `prop-card`), `tabular-nums tracking-tight` en el precio.
4. **Patch `SqlPreview.vue`** — añade `whitespace-nowrap` al `<h3>` "SQL generado" y al `<span>` del `tookMs`.
5. **Añade utilities en `assets/main.css`**: `.suggestion-chip`, refuerzo de `.input-search` con sombra + focus glow, `.prop-card` hover lift, `.hero-band` + `.hero-band::before` (textura puntos).
6. **Copy del subtitle** — actualiza en `SearchView.vue`: *"Escriba en español natural lo que busca. Traducimos su consulta a una búsqueda precisa sobre miles de propiedades — sin filtros, sin formularios."*
7. **Tests** — corre `npm run test:ci` después de cada paso grande. Si rompen selectores del wrapper, actualízalos. Agrega al menos 1 test por componente nuevo (Eyebrow, SuggestionChips, ResultBar).
8. **Type-check + build** — `npm run typecheck && npm run build` deben quedar limpios.

**Restricciones críticas:**

- **NO migres a React.** Todo en Vue 3 Composition API con `<script setup lang="ts">`.
- **NO toques** el store de Pinia, el axios client, los tipos OpenAPI, ni el contrato `/api/search`.
- **NO cambies** `ERROR_HINTS`, el loading skeleton, los placeholders rotatorios, ni el formato `Intl.NumberFormat('es-GT', { currency: 'USD' })`.
- **Mantén** usted-form, sentence case, sin emoji, sin signos de exclamación.
- **Mantén** la paleta — sólo azul confianza + terracota cálido + neutrals. Ni un color nuevo.
- **Sin librerías nuevas** (sin headless-ui, vueuse, etc.). Todo con Vue + Tailwind nativo.
- **Cobertura de tests** debe quedar ≥ 91% (hoy: 91.6%).

**Al terminar:**

- Marca el checklist al final del README como pasado.
- Reporta diferencias contra el target visual si las hay, con captura de pantalla.
- Si encuentras algún ambigüedad en el spec (ej. un radius que no está en config), pregunta antes de inventar.

Empieza leyendo el README y la estructura del codebase, después arma un plan corto antes de tocar código.
