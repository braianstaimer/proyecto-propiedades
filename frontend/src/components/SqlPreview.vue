<script setup lang="ts">
defineProps<{ sql: string; tookMs?: number | null }>()
</script>

<template>
  <section class="card p-5 bg-neutral-900 border-neutral-800" aria-label="SQL generado">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-caption text-neutral-400 font-mono uppercase tracking-wider whitespace-nowrap">SQL generado</h3>
      <span v-if="tookMs != null" class="text-caption text-neutral-500 font-mono whitespace-nowrap">
        {{ tookMs }} ms
      </span>
    </div>
    <pre class="text-caption font-mono text-primary-200 whitespace-pre-wrap break-all">{{ sql }}</pre>
  </section>
</template>
