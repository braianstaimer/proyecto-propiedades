<script setup lang="ts">
defineProps<{ showSql: boolean }>()
const emit = defineEmits<{ (e: 'toggle-sql'): void }>()
</script>

<template>
  <header class="bg-white border-b border-neutral-200 sticky top-0 z-10">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <svg class="w-9 h-9 text-primary-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M3 12 12 3l9 9" />
          <path d="M5 10v10h14V10" />
          <path d="M10 20v-5h4v5" />
        </svg>
        <div>
          <p class="text-h2 text-neutral-900 leading-tight">proyecto-propiedades</p>
          <p class="text-caption text-neutral-500">Búsqueda en lenguaje natural</p>
        </div>
      </div>
      <button
        type="button"
        class="btn-secondary text-caption"
        :aria-pressed="showSql"
        @click="emit('toggle-sql')"
      >
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <polyline points="16 18 22 12 16 6" />
          <polyline points="8 6 2 12 8 18" />
        </svg>
        {{ showSql ? 'Ocultar SQL' : 'Mostrar SQL' }}
      </button>
    </div>
  </header>
</template>
