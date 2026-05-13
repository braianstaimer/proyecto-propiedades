import { storeToRefs } from 'pinia'
import { useSearchStore } from '@/stores/search'

export function useSearch() {
  const store = useSearchStore()
  const { query, results, sql, tookMs, loading, error, hasSearched, isEmpty } = storeToRefs(store)

  async function search(text: string): Promise<void> {
    await store.search(text)
  }

  function reset(): void {
    store.reset()
  }

  return { query, results, sql, tookMs, loading, error, hasSearched, isEmpty, search, reset }
}
