<script setup lang="ts">
import { ref } from 'vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorAlert from '@/components/ErrorAlert.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import PropertyGrid from '@/components/PropertyGrid.vue'
import SearchBar from '@/components/SearchBar.vue'
import SqlPreview from '@/components/SqlPreview.vue'
import { useSearch } from '@/composables/useSearch'

defineProps<{ showSql: boolean }>()

const inputValue = ref('')
const { results, sql, tookMs, loading, error, hasSearched, isEmpty, search } = useSearch()

async function handleSubmit(): Promise<void> {
  await search(inputValue.value)
}

function dismissError(): void {
  if (error.value) error.value = null
}
</script>

<template>
  <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
    <section class="text-center mb-10">
      <h1 class="text-display text-neutral-900 mb-3">Encuentre su próxima propiedad</h1>
      <p class="text-body text-neutral-600 max-w-2xl mx-auto">
        Escriba en español natural lo que busca. Nuestra IA traduce su consulta a una búsqueda
        precisa sobre miles de propiedades.
      </p>
    </section>

    <section class="max-w-3xl mx-auto mb-10">
      <SearchBar v-model="inputValue" :loading="loading" @submit="handleSubmit" />
    </section>

    <section v-if="error" class="max-w-3xl mx-auto mb-8">
      <ErrorAlert :code="error.code" :message="error.message" @dismiss="dismissError" />
    </section>

    <section v-if="loading" aria-live="polite">
      <LoadingSpinner label="Buscando propiedades" />
    </section>

    <section v-else-if="isEmpty">
      <EmptyState :query="inputValue" />
    </section>

    <section v-else-if="hasSearched && results.length > 0" class="space-y-6">
      <div class="flex items-center justify-between">
        <p class="text-caption text-neutral-500">
          {{ results.length }} {{ results.length === 1 ? 'resultado' : 'resultados' }}
          <span v-if="tookMs != null"> · {{ tookMs }} ms</span>
        </p>
      </div>
      <SqlPreview v-if="showSql && sql" :sql="sql" :took-ms="tookMs" />
      <PropertyGrid :properties="results" />
    </section>
  </main>
</template>
