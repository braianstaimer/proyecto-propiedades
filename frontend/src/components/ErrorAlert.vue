<script setup lang="ts">
defineProps<{ code: string; message: string }>()
defineEmits<{ (e: 'dismiss'): void }>()

const ERROR_HINTS: Record<string, string> = {
  LLM_TIMEOUT: 'El modelo tardó demasiado. Reintente con una consulta más corta.',
  LLM_UNAVAILABLE: 'El servicio de IA no responde. Verifique que Ollama esté corriendo.',
  LLM_INVALID_OUTPUT: 'El modelo no generó un SQL válido. Reformule la consulta.',
  SQL_NOT_SELECT: 'La consulta generada no es de sólo lectura. Reformule.',
  SQL_FORBIDDEN_TABLE: 'La consulta intenta acceder a una tabla no permitida.',
  SQL_DANGEROUS_FUNCTION: 'La consulta usa funciones no permitidas.',
  EMPTY_QUERY: 'Ingrese una consulta entre 1 y 500 caracteres.',
  DB_ERROR: 'Error al consultar la base de datos. Reintente en unos segundos.',
  NETWORK_ERROR: 'No se pudo conectar con el servidor.',
  RATE_LIMIT: 'Demasiadas solicitudes. Espere un momento.',
}
</script>

<template>
  <div role="alert" class="bg-accent-50 border-l-4 border-accent-500 rounded-lg p-4 flex items-start gap-3">
    <svg class="w-5 h-5 text-accent-600 flex-shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
    <div class="flex-1">
      <p class="text-body font-semibold text-accent-800">{{ message }}</p>
      <p v-if="ERROR_HINTS[code]" class="text-caption text-accent-700 mt-1">
        {{ ERROR_HINTS[code] }}
      </p>
      <p class="text-caption text-accent-600 mt-2 font-mono">code: {{ code }}</p>
    </div>
    <button
      type="button"
      class="text-accent-700 hover:text-accent-900 p-1"
      aria-label="Cerrar"
      @click="$emit('dismiss')"
    >
      <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <line x1="18" y1="6" x2="6" y2="18" />
        <line x1="6" y1="6" x2="18" y2="18" />
      </svg>
    </button>
  </div>
</template>
