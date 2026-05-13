<script setup lang="ts">
defineProps<{ count: number; tookMs: number | null }>()
defineEmits<{ (e: 'reset'): void }>()
</script>

<template>
  <div class="flex items-center justify-between gap-3 pb-1">
    <div class="flex items-center gap-3">
      <span
        class="inline-flex items-center gap-2 pl-2 pr-3 py-1 rounded-full bg-white border border-neutral-200 text-sm font-semibold text-neutral-800 whitespace-nowrap"
      >
        <span class="w-2 h-2 rounded-full bg-primary-500 ring-[3px] ring-primary-500/20" />
        {{ count }} {{ count === 1 ? 'resultado' : 'resultados' }}
      </span>
      <span
        v-if="tookMs != null"
        class="font-mono text-xs text-neutral-500 whitespace-nowrap"
      >
        {{ tookMs }} ms
      </span>
    </div>
    <button type="button" class="btn-secondary" @click="$emit('reset')">
      Nueva búsqueda
    </button>
  </div>
</template>
