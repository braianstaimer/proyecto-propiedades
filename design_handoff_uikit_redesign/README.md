# Handoff · Rediseño del frontend proyecto-propiedades

> **Objetivo:** Aplicar el rediseño editorial del UI kit al frontend Vue existente, manteniendo Vue 3 + TypeScript + Tailwind + Pinia. NO migrar a React. NO crear archivos HTML nuevos en el repo final.

## Sobre los archivos de este paquete

Los archivos `.jsx` y `.html` incluidos son **referencias de diseño** — prototipos hechos en React para visualizar la dirección estética. **No los copies tal cual al repo.** La tarea es **reproducir esos diseños en los componentes Vue existentes** del codebase actual (`frontend/src/components/*.vue` y `frontend/src/views/SearchView.vue`), respetando:

- Vue 3.5 Composition API + `<script setup lang="ts">`
- Tailwind 3 utilities (`tailwind.config.ts` ya tiene los tokens)
- Pinia store (`stores/search.ts`)
- axios client (`services/api.ts`)
- Tipos generados (`types/api.ts`)
- Tests vitest + happy-dom existentes

## Fidelidad

**Alta fidelidad (hifi).** Colores, tipografía, radios y espaciados son finales. Reproduce los componentes pixel-perfect con utilities Tailwind. Cuando un valor no esté en `tailwind.config.ts`, agrégalo al config en vez de inline-arbitrary-values (excepto para sombras tinted que ya están en el config).

---

## Vistas afectadas

Una sola vista (`/`) — el SPA es de pantalla única. Los cambios viven en:

| Archivo Vue | Cambio | Detalles abajo |
|---|---|---|
| `frontend/src/views/SearchView.vue` | Reestructurar: hero band separado + main de resultados | [§ SearchView](#searchview) |
| `frontend/src/components/AppHeader.vue` | Sin cambios visuales | — |
| `frontend/src/components/SearchBar.vue` | Sombra sutil en input + glow en focus | [§ SearchBar](#searchbar) |
| `frontend/src/components/PropertyCard.vue` | Badge de tipo en gradient + hover lift + sin chip de tipo | [§ PropertyCard](#propertycard) |
| `frontend/src/components/SqlPreview.vue` | `whitespace-nowrap` en label + tiempo | [§ SqlPreview](#sqlpreview) |
| `frontend/src/components/EmptyState.vue` | Sin cambios | — |
| `frontend/src/components/ErrorAlert.vue` | Sin cambios | — |
| `frontend/src/components/LoadingSpinner.vue` | Sin cambios | — |
| **Nuevo:** `frontend/src/components/Eyebrow.vue` | Pill superior del hero | [§ Eyebrow](#eyebrow-nuevo) |
| **Nuevo:** `frontend/src/components/ResultBar.vue` | Chip + counter + reset | [§ ResultBar](#resultbar-nuevo) |
| **Nuevo:** `frontend/src/components/SuggestionChips.vue` | Chips bajo el SearchBar | [§ SuggestionChips](#suggestionchips-nuevo) |

---

## SearchView

### Layout actual (`views/SearchView.vue`)

Una `<main>` con hero centrado + SearchBar + sección de resultados, todo dentro de `max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12`.

### Layout nuevo

Dos bandas verticales:

1. **`.hero-band`** — wrapper full-bleed con textura. Dentro: `max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20`. Contiene `<Eyebrow>` + `<h1>` + subtitle + `<SearchBar>` + `<SuggestionChips>` (solo si `!hasSearched`).
2. **`<main>`** — `max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-9 pb-24`. Contiene `<ErrorAlert>`, `<LoadingSpinner>`, `<EmptyState>`, o el bloque de resultados (`<ResultBar>` + `<SqlPreview>` + `<PropertyGrid>`).

### Estilos de `.hero-band` (Tailwind + estilos custom)

Agregar al `<style scoped>` del SearchView o a un layer global en `assets/main.css`:

```css
.hero-band {
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid theme('colors.neutral.200');
  background:
    radial-gradient(60% 80% at 50% 0%, rgb(17 131 237 / 0.07), transparent 60%),
    radial-gradient(50% 50% at 92% 18%, rgb(221 88 50 / 0.05), transparent 60%),
    radial-gradient(50% 60% at 6% 80%, rgb(8 102 203 / 0.04), transparent 60%);
}
.hero-band::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image: radial-gradient(rgb(15 58 110 / 0.07) 1px, transparent 1px);
  background-size: 22px 22px;
  mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, #000 30%, transparent 75%);
  -webkit-mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, #000 30%, transparent 75%);
  opacity: 0.65;
}
.hero-band-inner { position: relative; }   /* asegura z-index sobre ::before */
```

### Hero

- **Eyebrow** (centrado): pill `inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary-50 border border-primary-200 text-primary-700 text-caption font-medium whitespace-nowrap`. Antes del texto, un círculo `w-1.5 h-1.5 rounded-full bg-current ring-4 ring-primary-50`. Texto: **"Búsqueda con IA · LLM local + SQL validado"**.
- **`<h1>` display**: `text-5xl sm:text-6xl md:text-7xl font-bold tracking-tight text-neutral-900 text-balance leading-[1.02]`. Texto: **"Encuentre su próxima propiedad"** (mismo que hoy). `margin-bottom: 1rem`.
- **Subtitle**: `text-base sm:text-lg text-neutral-600 max-w-xl mx-auto leading-relaxed`. Texto actualizado: **"Escriba en español natural lo que busca. Traducimos su consulta a una búsqueda precisa sobre miles de propiedades — sin filtros, sin formularios."**

Aumentar el `mb` entre eyebrow → h1 → subtitle a `mb-5 mb-4` respectivamente.

### Search section

`SearchBar` con `max-w-2xl mx-auto` (igual que hoy) seguido de `<SuggestionChips>` **siempre visible** (no condicional). Las sugerencias actúan como guía permanente para los patrones de consulta soportados — incluso después de buscar, el usuario puede refinar usando otra plantilla.

---

## SearchBar

Cambio mínimo en `frontend/src/components/SearchBar.vue`. La utility `.input-search` en `assets/main.css` recibe una sombra base + glow en focus:

```css
.input-search {
  @apply w-full px-5 py-4 rounded-xl bg-white border-2 border-neutral-200
    text-body text-neutral-900 placeholder:text-neutral-400
    focus:border-primary-500 focus:outline-none
    transition-colors duration-150;
  box-shadow: var(--shadow-card, 0 1px 3px 0 rgb(15 58 110 / 0.08));
}
.input-search:focus {
  box-shadow:
    0 0 0 4px rgb(17 131 237 / 0.08),
    0 1px 3px 0 rgb(15 58 110 / 0.08);
}
```

El botón `Buscar` no cambia.

---

## PropertyCard

Cambios en `frontend/src/components/PropertyCard.vue`:

### 1. Badge de tipo en el gradient (NUEVO)

Dentro del `<div>` del aspect-ratio gradient, posicionar **absoluto top-left** una pill blanca:

```html
<div class="aspect-[16/10] bg-gradient-to-br relative ..." :class="gradientByTipo[property.tipo]">
  <span class="absolute top-3 left-3 inline-flex items-center gap-1.5 px-2.5 py-1
               rounded-full bg-white/92 backdrop-blur-sm text-[11px] font-semibold
               text-neutral-800 shadow-sm">
    <component :is="iconForBadge" class="w-3 h-3 text-neutral-500" />
    {{ tipoLabel }}
  </span>
  <svg class="w-16 h-16 text-white/90" ... />
</div>
```

Donde:
- `bg-white/92` = `rgb(255 255 255 / 0.92)` (extender Tailwind si no existe el opacity step).
- `tipoLabel` = label español capitalizado: `Casa`, `Departamento`, `Terreno`, `Oficina`, `Local`.
- El icono pequeño es el mismo del gradient grande, pero a `w-3 h-3 stroke-2`.

### 2. Quitar el chip de tipo

En el `<div>` de chips, ELIMINA `<span class="chip capitalize">{{ property.tipo }}</span>`. El badge ya lo dice. Mantén los chips de `habitaciones`, `banos`, `area_m2`.

### 3. Hover lift

Agregar al `.card` (en `assets/main.css`) o sólo a `PropertyCard`:

```css
.prop-card {
  @apply will-change-transform transition-transform duration-200;
}
.prop-card:hover { transform: translateY(-3px); }
```

Y poner `class="card prop-card"` en el `<article>` raíz.

### 4. Tabular nums en precio + tracking

Al `<p>` del precio: `tabular-nums tracking-tight` (Tailwind). El `letterSpacing: '-0.01em'` se mapea a `tracking-tight` (o agregar custom).

### 5. h3 del título

`tracking-tight` para `letter-spacing: -0.005em` (suficiente). Mantén `text-h2 font-semibold leading-tight`.

---

## SqlPreview

`frontend/src/components/SqlPreview.vue` — solo agregar `whitespace-nowrap` al `<h3>` ("SQL generado") y al `<span>` del `tookMs`. Hoy con tracking-wider + uppercase se rompe en panel angosto.

---

## Eyebrow (nuevo)

`frontend/src/components/Eyebrow.vue` — pill reutilizable, soporta variante de color via prop:

```vue
<script setup lang="ts">
defineProps<{ tone?: 'primary' | 'accent' }>()
</script>
<template>
  <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full
               text-caption font-medium whitespace-nowrap border"
        :class="tone === 'accent'
          ? 'bg-accent-50 border-accent-200 text-accent-700'
          : 'bg-primary-50 border-primary-200 text-primary-700'">
    <span class="w-1.5 h-1.5 rounded-full bg-current"
          :class="tone === 'accent' ? 'ring-4 ring-accent-50' : 'ring-4 ring-primary-50'" />
    <slot />
  </span>
</template>
```

Uso: `<Eyebrow>Búsqueda con IA · LLM local + SQL validado</Eyebrow>`.

---

## ResultBar (nuevo)

`frontend/src/components/ResultBar.vue` — reemplaza el `<div>` con `text-caption` del SearchView actual:

```vue
<script setup lang="ts">
defineProps<{ count: number; tookMs: number | null }>()
defineEmits<{ (e: 'reset'): void }>()
</script>
<template>
  <div class="flex items-center justify-between gap-3 pb-1">
    <div class="flex items-center gap-3">
      <span class="inline-flex items-center gap-2 pl-2 pr-3 py-1 rounded-full
                   bg-white border border-neutral-200 text-sm font-semibold
                   text-neutral-800 whitespace-nowrap">
        <span class="w-2 h-2 rounded-full bg-primary-500 ring-[3px] ring-primary-500/20" />
        {{ count }} {{ count === 1 ? 'resultado' : 'resultados' }}
      </span>
      <span v-if="tookMs != null" class="font-mono text-xs text-neutral-500 whitespace-nowrap">
        {{ tookMs }} ms
      </span>
    </div>
    <button type="button" class="btn-secondary" @click="$emit('reset')">
      Nueva búsqueda
    </button>
  </div>
</template>
```

En `SearchView`, conectar `@reset` a un handler que llame `store.reset()` y borre el input local. (El store ya tiene `reset()` en `stores/search.ts`.)

---

## SuggestionChips (nuevo)

`frontend/src/components/SuggestionChips.vue` — **siempre visible** bajo el SearchBar como **grid de mini-cards** (3 cols × 2 rows en desktop). Cada card lleva un icono categórico + label uppercase del patrón + ejemplo de consulta. Los 6 ejemplos vienen del PDF del README raíz.

```vue
<script setup lang="ts">
import { MapPinIcon, TagIcon, ArrowsLeftRightIcon, SlidersIcon, CalendarIcon, SparklesIcon } from './icons'
// (Si no tienes una librería de iconos, copia los paths SVG inline — ver reference/Icons.jsx.)

const SUGGESTIONS = [
  { hint: 'Tipo + ubicación', query: 'Casas de 3 habitaciones en zona 10',         icon: MapPinIcon },
  { hint: 'Precio máximo',    query: 'Departamentos de menos de $150,000',         icon: TagIcon },
  { hint: 'Rango de precio',  query: 'Terrenos entre $50,000 y $100,000',          icon: ArrowsLeftRightIcon },
  { hint: 'Características',  query: 'Propiedades con más de 2 baños y 150 m²',    icon: SlidersIcon },
  { hint: 'Fecha',            query: 'Casas publicadas en los últimos 30 días',    icon: CalendarIcon },
  { hint: 'Combinada',        query: 'Departamentos con 2 habitaciones en zona 15', icon: SparklesIcon },
] as const

defineEmits<{ (e: 'pick', query: string): void }>()
</script>

<template>
  <div class="mt-7 flex flex-col gap-3.5">
    <div class="flex items-baseline justify-between gap-3 flex-wrap px-1">
      <span class="suggestions-label">
        Opciones sugeridas
      </span>
      <span class="text-xs text-neutral-500">
        Patrones que entendemos · haga clic para probar
      </span>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
      <button v-for="s in SUGGESTIONS" :key="s.query" type="button"
              class="suggestion-card" @click="$emit('pick', s.query)">
        <span class="suggestion-card__icon">
          <component :is="s.icon" class="w-4 h-4" />
        </span>
        <span class="flex flex-col gap-[3px] min-w-0 flex-1">
          <span class="suggestion-card__hint">{{ s.hint }}</span>
          <span class="suggestion-card__query">{{ s.query }}</span>
        </span>
      </button>
    </div>
  </div>
</template>
```

Utilities en `assets/main.css`:

```css
.suggestions-label {
  @apply text-[11px] tracking-[0.1em] uppercase font-semibold text-primary-700
    whitespace-nowrap inline-flex items-center gap-2;
}
.suggestions-label::before {
  content: ''; display: inline-block; width: 16px; height: 1px;
  background: currentColor; opacity: 0.5;
}

.suggestion-card {
  @apply flex items-start gap-3 px-3.5 py-3 rounded-lg
    bg-white/70 backdrop-blur-sm border border-neutral-200
    text-left cursor-pointer
    hover:bg-white hover:border-primary-200
    transition-all duration-150;
}
.suggestion-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px -8px rgb(15 58 110 / 0.18);
}
.suggestion-card__icon {
  @apply inline-flex items-center justify-center w-[30px] h-[30px] rounded-lg
    bg-primary-50 text-primary-700 shrink-0;
}
.suggestion-card__hint {
  @apply text-[10.5px] tracking-[0.08em] uppercase font-semibold text-neutral-500;
}
.suggestion-card__query {
  @apply text-[13.5px] leading-snug font-medium text-neutral-800;
}
```

**Iconos requeridos** (Lucide-style, stroke 2, viewBox 24x24): `map-pin`, `tag`, `arrows-left-right` (o `arrow-left-right`), `sliders-horizontal`, `calendar`, `sparkles`. Sus paths exactos están en `reference/Icons.jsx` y son los mismos que usa el kit.

En `SearchView`, cuando el usuario hace click en una sugerencia: `inputValue.value = s; await search(s)`. **El componente se mantiene visible incluso después de buscar** — el usuario puede usarlas para refinar la consulta en cualquier momento.

**Layout**: el contenedor padre debe ser `max-w-3xl mx-auto` para el SearchBar pero `max-w-4xl mx-auto` para el grid de sugerencias (más ancho permite cards más cómodas). En el template del SearchView, envuélvelos en una `<section>` `max-w-4xl mx-auto` y pon el SearchBar dentro de un `max-w-3xl mx-auto` interno.

---

## Estados (no cambian)

- **Loading** — sigue siendo `LoadingSpinner.vue` (skeleton de 3 cards). Pixel-perfect ya está bien.
- **Empty** — `EmptyState.vue` igual.
- **Error** — `ErrorAlert.vue` igual.

---

## Design tokens (referencia rápida)

Todos ya están en `frontend/tailwind.config.ts`. No cambian.

**Colores**

| Token | Hex |
|---|---|
| `primary-50` | `#f0f7ff` |
| `primary-100` | `#e0eefe` |
| `primary-200` | `#bcdcfd` |
| `primary-500` | `#1183ed` |
| `primary-700` | `#0850a3` |
| `primary-800` | `#0b4585` |
| `accent-50` | `#fdf5f0` |
| `accent-200` | `#f4c9b1` |
| `accent-500` | `#dd5832` |
| `accent-700` | `#a93420` |
| neutrals 50–900 | Tailwind defaults extendidas |

**Tipo**: Inter (400/500/600/700) + JetBrains Mono (400/600). Carga vía Google Fonts (ya está en `index.html`).

**Radii**: `xl: 0.875rem` (14px), `2xl: 1.25rem` (20px). Ya en config.

**Sombras**: `shadow-card`, `shadow-card-hover`. Ya en config — son tinted con `rgb(15 58 110 / α)`.

**Escala tipográfica custom**: `text-display | text-h1 | text-h2 | text-body | text-caption`. Ya en config.

---

## Interacciones / motion

- **Hover de cards**: `translateY(-3px)` + cambio de `shadow-card → shadow-card-hover`, 200ms ease.
- **Press de botones primarios**: `active:scale-[0.99]` (ya existe).
- **Suggestion chips**: `active:scale-[0.97]`.
- **Transiciones**: 150ms para color, 200ms para sombras. Easing Tailwind default.
- **Sin entrance animations** en cards (el kit tenía stagger pero lo quitamos — opcional reinstalar con CSS `@keyframes fadeUp` y `--i` por card).
- **Sin scroll-linked, parallax, springs.** El producto se mantiene tranquilo.

---

## Copy

- **Eyebrow**: `Búsqueda con IA · LLM local + SQL validado`
- **H1**: `Encuentre su próxima propiedad` (sin cambio)
- **Subtitle nuevo**: `Escriba en español natural lo que busca. Traducimos su consulta a una búsqueda precisa sobre miles de propiedades — sin filtros, sin formularios.`
- **Sugerencias** (3): listadas arriba en `SuggestionChips`.
- **Counter**: `{n} {n===1 ? 'resultado' : 'resultados'}`
- **Reset button**: `Nueva búsqueda`
- Tono: usted-form, sentence case, sin emoji, sin signos de exclamación.

---

## Assets

- **Logo**: `frontend/public/favicon.svg` ya tiene el house glyph. No cambia.
- **Iconos**: inline SVG con stroke 2 (1.5 para hero glyphs, 2.4 para logo). Mantén el patrón actual de `PropertyCard.vue` (`iconByTipo` map + `gradientByTipo`).
- **Sin imágenes nuevas.** El tipo gradient sigue siendo la única "imagen" del card.

---

## Tests

Los 20 tests vitest existentes deben seguir pasando. Cambios esperados:

- `SearchView.spec.ts` — actualizar selectores del wrapper si pasaron de `<section>` a la nueva estructura hero-band. La lógica (loading/empty/error/success) no cambia.
- Agregar tests nuevos para los 3 componentes nuevos (`Eyebrow`, `ResultBar`, `SuggestionChips`) — al menos 1 test por uno.
- Reset desde `ResultBar` debe llamar `store.reset()`.

Objetivo: mantener coverage ≥ 91% (actual: 91.6%).

---

## Archivos de referencia incluidos en este paquete

| Archivo | Para qué sirve |
|---|---|
| `reference/index.html` | El UI kit completo renderizado. Abrirlo en un navegador para ver el resultado esperado. |
| `reference/SearchView.jsx` | Layout final del hero band + main de resultados (React). Léelo como **referencia visual**, no copies. |
| `reference/PropertyCard.jsx` | Card con tipo badge + hover lift + tabular nums (React). |
| `reference/Feedback.jsx` | ErrorAlert, EmptyState, LoadingSkeleton, SqlPreview (React). El SqlPreview es el cambio clave. |
| `reference/SearchBar.jsx` | El search bar con placeholder rotatorio + el botón loading. |
| `reference/Logo.jsx`, `AppHeader.jsx`, `Icons.jsx` | Sin cambios visuales — pero útil para confirmar paths SVG de cada tipo. |
| `reference/colors_and_type.css` | Tokens del design system (espejo de Tailwind config). |
| `reference/MOCK_DATA.js` | Datos de prueba. Útil si quieres seed data de exploración. |

---

## Checklist de entrega

- [ ] `SearchView.vue` reestructurada en hero-band + main
- [ ] `Eyebrow.vue` creado
- [ ] `SuggestionChips.vue` creado + handler en SearchView
- [ ] `ResultBar.vue` creado + reemplaza el counter inline
- [ ] `PropertyCard.vue` con badge de tipo + hover lift + tipo chip removido
- [ ] `SqlPreview.vue` con `whitespace-nowrap` en header y timing
- [ ] `.input-search` con sombra + focus glow en `assets/main.css`
- [ ] `.suggestion-chip` utility en `assets/main.css`
- [ ] `.hero-band` + textura en CSS (scoped o global)
- [ ] Copy del subtitle actualizada
- [ ] Tests pasando con cobertura ≥ 91%
- [ ] `npm run typecheck` limpio
- [ ] `npm run build` sin warnings nuevos

---

## Lo que NO debe cambiar

- Pinia store, axios client, tipos OpenAPI.
- El contrato `/api/search` (request/response shape).
- Las traducciones de error codes (`ERROR_HINTS` en `ErrorAlert`).
- Loading skeleton (3 cards `animate-pulse`).
- `tailwind.config.ts` excepto si necesitas un opacity step nuevo (`white/92`) o un weight extra de Inter (800).
