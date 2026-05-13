import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { mount, flushPromises } from '@vue/test-utils'
import SearchView from '@/views/SearchView.vue'

vi.mock('@/services/api', async () => {
  const actual = await vi.importActual<typeof import('@/services/api')>('@/services/api')
  return {
    ...actual,
    searchProperties: vi.fn(),
  }
})

import { searchProperties } from '@/services/api'
import { ApiError } from '@/services/api'

const mockedSearch = vi.mocked(searchProperties)

function mountView(props: { showSql?: boolean } = {}) {
  return mount(SearchView, {
    props: { showSql: props.showSql ?? false },
  })
}

describe('SearchView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    mockedSearch.mockReset()
  })

  it('renders header copy and search bar', () => {
    const wrapper = mountView()
    expect(wrapper.text()).toContain('Encuentre su próxima propiedad')
    expect(wrapper.find('input[type="search"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('renders LoadingSpinner while searching', async () => {
    mockedSearch.mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(
            () =>
              resolve({
                query: 'x',
                sql: 'SELECT 1 FROM propiedades',
                count: 0,
                results: [],
                took_ms: 1,
              }),
            50,
          )
        }),
    )
    const wrapper = mountView()
    await wrapper.find('input[type="search"]').setValue('Busco casas')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    // While the promise is pending, loading=true. Look for status role.
    expect(wrapper.find('[role="status"]').exists() || wrapper.text().includes('Buscando')).toBe(true)
  })

  it('renders EmptyState after search with zero results', async () => {
    mockedSearch.mockResolvedValue({
      query: 'x',
      sql: 'SELECT 1 FROM propiedades',
      count: 0,
      results: [],
      took_ms: 1,
    })
    const wrapper = mountView()
    await wrapper.find('input[type="search"]').setValue('algo raro')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(wrapper.text()).toContain('Sin resultados')
  })

  it('renders ErrorAlert with code message on API error', async () => {
    mockedSearch.mockRejectedValue(new ApiError('LLM_TIMEOUT', 'tarde', 422))
    const wrapper = mountView()
    await wrapper.find('input[type="search"]').setValue('algo')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(wrapper.text()).toContain('tarde')
    expect(wrapper.text()).toContain('LLM_TIMEOUT')
  })

  it('shows SqlPreview when showSql=true and results exist', async () => {
    mockedSearch.mockResolvedValue({
      query: 'x',
      sql: 'SELECT id FROM propiedades LIMIT 1',
      count: 1,
      results: [
        {
          id: 1,
          titulo: 'Casa A',
          descripcion: 'desc',
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
    const wrapper = mountView({ showSql: true })
    await wrapper.find('input[type="search"]').setValue('Busco casas')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(wrapper.text()).toContain('SQL generado')
    expect(wrapper.text()).toContain('SELECT id FROM propiedades')
  })

  it('hides SqlPreview when showSql=false', async () => {
    mockedSearch.mockResolvedValue({
      query: 'x',
      sql: 'SELECT id FROM propiedades LIMIT 1',
      count: 1,
      results: [
        {
          id: 1,
          titulo: 'Casa A',
          descripcion: null,
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
    const wrapper = mountView({ showSql: false })
    await wrapper.find('input[type="search"]').setValue('Busco casas')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(wrapper.text()).not.toContain('SQL generado')
  })

  it('runs a search when a suggestion chip is picked', async () => {
    mockedSearch.mockResolvedValue({
      query: 'Casas de 3 habitaciones en zona 10',
      sql: 'SELECT id FROM propiedades LIMIT 1',
      count: 1,
      results: [
        {
          id: 1,
          titulo: 'Casa Suggested',
          descripcion: null,
          tipo: 'casa',
          precio: 100000,
          habitaciones: 3,
          banos: 2,
          area_m2: 150,
          ubicacion: 'Zona 10',
          fecha_publicacion: '2026-04-21',
        },
      ],
      took_ms: 80,
    })
    const wrapper = mountView()
    const suggestionButton = wrapper
      .findAll('button')
      .find((b) => b.text().includes('Casas de 3 habitaciones en zona 10'))
    expect(suggestionButton).toBeDefined()
    await suggestionButton!.trigger('click')
    await flushPromises()

    expect(mockedSearch).toHaveBeenCalledTimes(1)
    expect(mockedSearch).toHaveBeenCalledWith({
      query: 'Casas de 3 habitaciones en zona 10',
    })
    const input = wrapper.find('input[type="search"]')
      .element as HTMLInputElement
    expect(input.value).toBe('Casas de 3 habitaciones en zona 10')
    expect(wrapper.text()).toContain('1 resultado')
    expect(wrapper.text()).toContain('Casa Suggested')
  })

  it('clears results and input when ResultBar emits reset', async () => {
    mockedSearch.mockResolvedValue({
      query: 'x',
      sql: 'SELECT id FROM propiedades LIMIT 1',
      count: 1,
      results: [
        {
          id: 1,
          titulo: 'Casa A',
          descripcion: null,
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
    const wrapper = mountView()
    await wrapper.find('input[type="search"]').setValue('Busco casas')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(wrapper.text()).toContain('Casa A')

    const resetButton = wrapper
      .findAll('button')
      .find((b) => b.text() === 'Nueva búsqueda')
    expect(resetButton).toBeDefined()
    await resetButton!.trigger('click')
    await flushPromises()

    expect(wrapper.text()).not.toContain('Casa A')
    const input = wrapper.find('input[type="search"]')
      .element as HTMLInputElement
    expect(input.value).toBe('')
  })

  it('dismisses error when clicking close button', async () => {
    mockedSearch.mockRejectedValue(new ApiError('LLM_TIMEOUT', 'msg', 422))
    const wrapper = mountView()
    await wrapper.find('input[type="search"]').setValue('algo')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(wrapper.text()).toContain('msg')
    const dismissBtn = wrapper.find('[aria-label="Cerrar"]')
    expect(dismissBtn.exists()).toBe(true)
    await dismissBtn.trigger('click')
    await flushPromises()
    expect(wrapper.text()).not.toContain('msg')
  })
})
