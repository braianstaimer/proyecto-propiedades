<script setup lang="ts">
import { ref } from 'vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorAlert from '@/components/ErrorAlert.vue'
import Eyebrow from '@/components/Eyebrow.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import PropertyGrid from '@/components/PropertyGrid.vue'
import ResultBar from '@/components/ResultBar.vue'
import SearchBar from '@/components/SearchBar.vue'
import SqlPreview from '@/components/SqlPreview.vue'
import SuggestionChips from '@/components/SuggestionChips.vue'
import { useSearch } from '@/composables/useSearch'

defineProps<{ showSql: boolean }>()

const inputValue = ref('')
const { results, sql, tookMs, loading, error, hasSearched, isEmpty, search, reset } =
  useSearch()

async function handleSubmit(): Promise<void> {
  await search(inputValue.value)
}

async function handleSuggestion(query: string): Promise<void> {
  inputValue.value = query
  await search(query)
}

function handleReset(): void {
  reset()
  inputValue.value = ''
}

function dismissError(): void {
  if (error.value) error.value = null
}
</script>

<template>
  <div class="hero-band" :class="{ 'hero-band--compact': hasSearched }">
    <div
      class="hero-band-inner max-w-6xl mx-auto px-4 sm:px-6 lg:px-8"
      :class="hasSearched ? 'py-6 sm:py-8' : 'py-10 sm:py-14'"
    >
      <section v-if="!hasSearched" class="text-center">
        <Eyebrow class="mb-4">Búsqueda con IA · LLM local + SQL validado</Eyebrow>
        <h1
          class="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight text-neutral-900 text-balance leading-[1.05] mb-3"
        >
          Encuentre su próxima propiedad
        </h1>
        <p class="text-base sm:text-lg text-neutral-600 max-w-xl mx-auto leading-relaxed">
          Escriba en español natural lo que busca. Traducimos su consulta a una búsqueda
          precisa sobre miles de propiedades — sin filtros, sin formularios.
        </p>
      </section>

      <section class="max-w-4xl mx-auto" :class="hasSearched ? '' : 'mt-8'">
        <div class="max-w-3xl mx-auto">
          <SearchBar v-model="inputValue" :loading="loading" @submit="handleSubmit" />
        </div>
        <SuggestionChips v-if="!hasSearched" @pick="handleSuggestion" />
      </section>
    </div>
  </div>

  <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-24">
    <section v-if="error" class="max-w-3xl mx-auto mb-8">
      <ErrorAlert :code="error.code" :message="error.message" @dismiss="dismissError" />
    </section>

    <section v-if="loading" aria-live="polite">
      <LoadingSpinner label="Buscando propiedades" />
    </section>

    <section v-if="!loading && !error && hasSearched && showSql && sql" class="mb-5">
      <SqlPreview :sql="sql" :took-ms="tookMs" />
    </section>

    <section v-if="isEmpty" class="flex flex-col gap-2">
      <EmptyState :query="inputValue" />
      <div class="max-w-4xl mx-auto w-full">
        <SuggestionChips @pick="handleSuggestion" />
      </div>
    </section>

    <section v-else-if="hasSearched && results.length > 0" class="flex flex-col gap-5">
      <ResultBar :count="results.length" :took-ms="tookMs" @reset="handleReset" />
      <PropertyGrid :properties="results" />
    </section>
  </main>
</template>
