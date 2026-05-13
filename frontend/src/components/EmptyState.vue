<script setup lang="ts">
defineProps<{ query?: string }>()
</script>

<template>
  <div class="card p-12 text-center max-w-2xl mx-auto">
    <svg class="w-16 h-16 mx-auto text-neutral-300 mb-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="11" cy="11" r="7" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
    <h2 class="text-h2 text-neutral-900 mb-2">Sin resultados</h2>
    <p v-if="query" class="text-body text-neutral-600">
      No encontramos propiedades para <strong class="text-neutral-900">"{{ query }}"</strong>.
    </p>
    <p v-else class="text-body text-neutral-600">No encontramos propiedades para esa búsqueda.</p>
    <p class="text-caption text-neutral-500 mt-4">
      Pruebe variando el tipo, la zona, el rango de precio o el número de habitaciones.
    </p>
  </div>
</template>
