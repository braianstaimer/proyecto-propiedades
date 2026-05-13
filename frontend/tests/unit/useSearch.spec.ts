import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSearch } from '@/composables/useSearch'
import { ApiError } from '@/services/api'

vi.mock('@/services/api', async () => {
  const actual = await vi.importActual<typeof import('@/services/api')>('@/services/api')
  return {
    ...actual,
    searchProperties: vi.fn(),
  }
})

import { searchProperties } from '@/services/api'

const mockedSearch = vi.mocked(searchProperties)

describe('useSearch', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    mockedSearch.mockReset()
  })

  it('starts with empty state', () => {
    const { results, loading, error, hasSearched } = useSearch()
    expect(results.value).toEqual([])
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
    expect(hasSearched.value).toBe(false)
  })

  it('populates results on 200', async () => {
    mockedSearch.mockResolvedValue({
      query: 'casa',
      sql: 'SELECT * FROM propiedades LIMIT 1',
      count: 1,
      results: [
        {
          id: 1,
          titulo: 'Casa X',
          descripcion: 'd',
          tipo: 'casa',
          precio: 100000,
          habitaciones: 3,
          banos: 2,
          area_m2: 150,
          ubicacion: 'Zona 10',
          fecha_publicacion: '2026-04-21',
        },
      ],
      took_ms: 100,
    })

    const { results, sql, tookMs, loading, hasSearched, search } = useSearch()
    await search('Busco casas')
    expect(results.value).toHaveLength(1)
    expect(sql.value).toContain('SELECT')
    expect(tookMs.value).toBe(100)
    expect(loading.value).toBe(false)
    expect(hasSearched.value).toBe(true)
  })

  it('sets error on API error with code', async () => {
    mockedSearch.mockRejectedValue(
      new ApiError('LLM_TIMEOUT', 'tarde', 422, 'req-1'),
    )

    const { error, results, hasSearched, search } = useSearch()
    await search('Busco casas')
    expect(error.value?.code).toBe('LLM_TIMEOUT')
    expect(error.value?.message).toBe('tarde')
    expect(results.value).toEqual([])
    expect(hasSearched.value).toBe(true)
  })

  it('clears previous results before new search', async () => {
    mockedSearch.mockResolvedValueOnce({
      query: 'a',
      sql: 'SELECT 1 FROM propiedades',
      count: 1,
      results: [
        {
          id: 1,
          titulo: 'A',
          descripcion: null,
          tipo: 'casa',
          precio: 1,
          habitaciones: 1,
          banos: 1,
          area_m2: 1,
          ubicacion: 'x',
          fecha_publicacion: '2026-01-01',
        },
      ],
      took_ms: 1,
    })

    const { results, search } = useSearch()
    await search('first')
    expect(results.value).toHaveLength(1)

    mockedSearch.mockResolvedValueOnce({
      query: 'b',
      sql: 'SELECT 1 FROM propiedades',
      count: 0,
      results: [],
      took_ms: 1,
    })
    await search('second')
    expect(results.value).toEqual([])
  })

  it('ignores empty query', async () => {
    const { search, hasSearched } = useSearch()
    await search('   ')
    expect(mockedSearch).not.toHaveBeenCalled()
    expect(hasSearched.value).toBe(false)
  })

  it('isEmpty true after search with zero results', async () => {
    mockedSearch.mockResolvedValue({
      query: 'x',
      sql: 'SELECT 1 FROM propiedades',
      count: 0,
      results: [],
      took_ms: 1,
    })
    const { search, isEmpty } = useSearch()
    await search('x')
    expect(isEmpty.value).toBe(true)
  })

  it('reset clears state', async () => {
    mockedSearch.mockResolvedValue({
      query: 'x',
      sql: 'SELECT 1 FROM propiedades',
      count: 1,
      results: [
        {
          id: 1,
          titulo: 'A',
          descripcion: null,
          tipo: 'casa',
          precio: 1,
          habitaciones: null,
          banos: null,
          area_m2: null,
          ubicacion: 'x',
          fecha_publicacion: '2026-01-01',
        },
      ],
      took_ms: 1,
    })
    const { search, reset, results, hasSearched } = useSearch()
    await search('x')
    expect(results.value).toHaveLength(1)
    reset()
    expect(results.value).toEqual([])
    expect(hasSearched.value).toBe(false)
  })
})
