import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { ApiError, searchProperties } from '@/services/api'
import type { PropertyOut } from '@/types/api'

export const useSearchStore = defineStore('search', () => {
  const query = ref('')
  const results = ref<PropertyOut[]>([])
  const sql = ref<string | null>(null)
  const tookMs = ref<number | null>(null)
  const loading = ref(false)
  const error = ref<{ code: string; message: string } | null>(null)
  const hasSearched = ref(false)

  const isEmpty = computed(() => hasSearched.value && results.value.length === 0 && !loading.value && !error.value)

  async function search(rawQuery: string): Promise<void> {
    const q = rawQuery.trim()
    if (!q) return
    loading.value = true
    error.value = null
    results.value = []
    sql.value = null
    tookMs.value = null
    query.value = q
    try {
      const response = await searchProperties({ query: q })
      results.value = response.results
      sql.value = response.sql
      tookMs.value = response.took_ms
    } catch (err) {
      if (err instanceof ApiError) {
        error.value = { code: err.code, message: err.message }
      } else {
        error.value = { code: 'UNKNOWN_ERROR', message: 'Error inesperado.' }
      }
    } finally {
      loading.value = false
      hasSearched.value = true
    }
  }

  function reset(): void {
    query.value = ''
    results.value = []
    sql.value = null
    tookMs.value = null
    loading.value = false
    error.value = null
    hasSearched.value = false
  }

  return { query, results, sql, tookMs, loading, error, hasSearched, isEmpty, search, reset }
})
