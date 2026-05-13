<script setup lang="ts">
defineProps<{ label?: string }>()
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" role="status" :aria-label="label || 'Cargando resultados'">
    <div v-for="n in 3" :key="n" class="card overflow-hidden">
      <div class="aspect-[16/10] bg-neutral-100 animate-pulse" />
      <div class="p-5 flex flex-col gap-3">
        <div class="h-5 bg-neutral-100 rounded animate-pulse w-3/4" />
        <div class="h-4 bg-neutral-100 rounded animate-pulse w-full" />
        <div class="flex gap-2 pt-2">
          <div class="h-6 w-16 bg-neutral-100 rounded-full animate-pulse" />
          <div class="h-6 w-16 bg-neutral-100 rounded-full animate-pulse" />
        </div>
      </div>
    </div>
  </div>
</template>
