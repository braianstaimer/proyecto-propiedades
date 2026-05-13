<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'

const props = defineProps<{ loading: boolean; modelValue: string }>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'submit'): void
}>()

const placeholders = [
  'Busco casas de 3 habitaciones en zona 10',
  'Muéstrame departamentos de menos de $150,000',
  'Propiedades con más de 2 baños y al menos 150 m²',
  'Casas publicadas en los últimos 30 días',
  'Terrenos entre $50,000 y $100,000',
]
const index = ref(0)
let intervalId: ReturnType<typeof setInterval> | null = null

const placeholder = computed(() => placeholders[index.value % placeholders.length])

onMounted(() => {
  intervalId = setInterval(() => {
    index.value = (index.value + 1) % placeholders.length
  }, 4000)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}

function onSubmit() {
  if (!props.loading && props.modelValue.trim()) emit('submit')
}
</script>

<template>
  <form
    role="search"
    class="w-full flex flex-col sm:flex-row gap-3"
    @submit.prevent="onSubmit"
  >
    <label class="sr-only" for="search-input">Consulta de propiedades</label>
    <div class="relative flex-1">
      <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="11" cy="11" r="7" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
      <input
        id="search-input"
        type="search"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="loading"
        class="input-search pl-12"
        maxlength="500"
        autocomplete="off"
        spellcheck="true"
        @input="onInput"
      />
    </div>
    <button
      type="submit"
      class="btn-primary"
      :disabled="loading || !modelValue.trim()"
      aria-label="Buscar propiedades"
    >
      <span v-if="!loading">Buscar</span>
      <span v-else class="inline-flex items-center gap-2">
        <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <circle cx="12" cy="12" r="10" stroke-opacity=".25" />
          <path d="M22 12a10 10 0 0 1-10 10" />
        </svg>
        Buscando…
      </span>
    </button>
  </form>
</template>
