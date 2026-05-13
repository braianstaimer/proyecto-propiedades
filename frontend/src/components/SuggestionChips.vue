<script setup lang="ts">
interface Suggestion {
  hint: string
  query: string
  svg: string
}

const SUGGESTIONS: readonly Suggestion[] = [
  {
    hint: 'Tipo + ubicación',
    query: 'Casas de 3 habitaciones en zona 10',
    svg: '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" /><circle cx="12" cy="10" r="3" />',
  },
  {
    hint: 'Precio máximo',
    query: 'Departamentos de menos de $150,000',
    svg: '<path d="M20.59 13.41 13.42 20.58a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" /><line x1="7" y1="7" x2="7.01" y2="7" />',
  },
  {
    hint: 'Rango de precio',
    query: 'Terrenos entre $50,000 y $100,000',
    svg: '<path d="m16 3 4 4-4 4" /><path d="M20 7H4" /><path d="m8 21-4-4 4-4" /><path d="M4 17h16" />',
  },
  {
    hint: 'Características',
    query: 'Propiedades con más de 2 baños y 150 m²',
    svg: '<line x1="4" y1="21" x2="4" y2="14" /><line x1="4" y1="10" x2="4" y2="3" /><line x1="12" y1="21" x2="12" y2="12" /><line x1="12" y1="8" x2="12" y2="3" /><line x1="20" y1="21" x2="20" y2="16" /><line x1="20" y1="12" x2="20" y2="3" /><line x1="1" y1="14" x2="7" y2="14" /><line x1="9" y1="8" x2="15" y2="8" /><line x1="17" y1="16" x2="23" y2="16" />',
  },
  {
    hint: 'Fecha',
    query: 'Casas publicadas en los últimos 30 días',
    svg: '<rect x="3" y="4" width="18" height="18" rx="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />',
  },
  {
    hint: 'Combinada',
    query: 'Departamentos con 2 habitaciones en zona 15',
    svg: '<path d="M12 3v3 M12 18v3 M3 12h3 M18 12h3 M5.6 5.6 7.7 7.7 M16.3 16.3 18.4 18.4 M5.6 18.4 7.7 16.3 M16.3 7.7 18.4 5.6" />',
  },
]

defineEmits<{ (e: 'pick', query: string): void }>()
</script>

<template>
  <div class="mt-7 flex flex-col gap-3.5">
    <div class="flex items-baseline justify-between gap-3 flex-wrap px-1">
      <span class="suggestions-label">Opciones sugeridas</span>
      <span class="text-xs text-neutral-500">
        Patrones que entendemos · haga clic para probar
      </span>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
      <button
        v-for="s in SUGGESTIONS"
        :key="s.query"
        type="button"
        class="suggestion-card"
        @click="$emit('pick', s.query)"
      >
        <span class="suggestion-card__icon">
          <svg
            class="w-4 h-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
            v-html="s.svg"
          />
        </span>
        <span class="flex flex-col gap-[3px] min-w-0 flex-1">
          <span class="suggestion-card__hint">{{ s.hint }}</span>
          <span class="suggestion-card__query">{{ s.query }}</span>
        </span>
      </button>
    </div>
  </div>
</template>
