/**
 * Smoke tests · golden path frontend.
 *
 * Valida render del shell + integración store + bandera de error humanizada.
 * No reemplazan los unit tests (que cubren edge cases); estos son el subset
 * mínimo que debe pasar para que se considere un build releasable.
 *
 * Se corren con `npm run test:smoke` (configurado en package.json).
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { flushPromises, mount } from '@vue/test-utils'
import SearchView from '@/views/SearchView.vue'
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

function mountView(showSql = false) {
  return mount(SearchView, { props: { showSql } })
}

const SAMPLE_PROPERTY = {
  id: 1,
  titulo: 'Casa moderna en Zona 10',
  descripcion: 'Acabados de lujo',
  tipo: 'casa' as const,
  precio: 320000,
  habitaciones: 3,
  banos: 3,
  area_m2: 240,
  ubicacion: 'Zona 10, Guatemala',
  fecha_publicacion: '2026-04-21',
}

describe('smoke · golden path UI', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    mockedSearch.mockReset()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renderiza shell con SearchBar y mensaje hero', () => {
    const wrapper = mountView()
    expect(wrapper.text()).toContain('Encuentre su próxima propiedad')
    expect(wrapper.find('input[type="search"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('búsqueda happy path: respuesta 200 pinta cards', async () => {
    mockedSearch.mockResolvedValue({
      query: 'Busco casas',
      sql: 'SELECT id, titulo FROM propiedades LIMIT 1',
      count: 1,
      results: [SAMPLE_PROPERTY],
      took_ms: 1500,
    })

    const wrapper = mountView()
    await wrapper.find('input[type="search"]').setValue('Busco casas')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Casa moderna en Zona 10')
    expect(wrapper.text()).toContain('Zona 10, Guatemala')
    expect(wrapper.text()).toContain('1 resultado')
  })

  it('toggle SqlPreview muestra el SQL cuando showSql=true', async () => {
    mockedSearch.mockResolvedValue({
      query: 'Busco casas',
      sql: 'SELECT id, titulo FROM propiedades LIMIT 1',
      count: 1,
      results: [SAMPLE_PROPERTY],
      took_ms: 100,
    })

    const wrapper = mountView(true)
    await wrapper.find('input[type="search"]').setValue('Busco casas')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('SQL generado')
    expect(wrapper.text()).toContain('SELECT id, titulo FROM propiedades')
  })

  it('estado vacío: respuesta 200 con results=[] muestra EmptyState', async () => {
    mockedSearch.mockResolvedValue({
      query: 'algo raro',
      sql: 'SELECT 1 FROM propiedades LIMIT 0',
      count: 0,
      results: [],
      took_ms: 100,
    })

    const wrapper = mountView()
    await wrapper.find('input[type="search"]').setValue('algo raro')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Sin resultados')
  })

  it('estado error: ApiError con code se humaniza en ErrorAlert', async () => {
    mockedSearch.mockRejectedValue(new ApiError('LLM_TIMEOUT', 'El modelo tardó', 422, 'req-1'))

    const wrapper = mountView()
    await wrapper.find('input[type="search"]').setValue('Busco casas')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('El modelo tardó')
    expect(wrapper.text()).toContain('LLM_TIMEOUT')
  })

  it('dismiss del ErrorAlert limpia el banner', async () => {
    mockedSearch.mockRejectedValue(new ApiError('LLM_TIMEOUT', 'tarde', 422))

    const wrapper = mountView()
    await wrapper.find('input[type="search"]').setValue('algo')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(wrapper.text()).toContain('tarde')

    await wrapper.find('[aria-label="Cerrar"]').trigger('click')
    await flushPromises()
    expect(wrapper.text()).not.toContain('tarde')
  })
})
