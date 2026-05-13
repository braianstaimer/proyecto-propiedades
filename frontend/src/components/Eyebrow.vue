<script setup lang="ts">
defineProps<{ tone?: 'primary' | 'accent' }>()
</script>

<template>
  <span
    class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-caption font-medium whitespace-nowrap border"
    :class="
      tone === 'accent'
        ? 'bg-accent-50 border-accent-200 text-accent-700'
        : 'bg-primary-50 border-primary-200 text-primary-700'
    "
  >
    <span
      class="w-1.5 h-1.5 rounded-full bg-current"
      :class="tone === 'accent' ? 'ring-4 ring-accent-50' : 'ring-4 ring-primary-50'"
    />
    <slot />
  </span>
</template>
