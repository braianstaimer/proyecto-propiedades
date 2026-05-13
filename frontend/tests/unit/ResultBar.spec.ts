import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ResultBar from '@/components/ResultBar.vue'

describe('ResultBar', () => {
  it('renders singular label with one result', () => {
    const wrapper = mount(ResultBar, { props: { count: 1, tookMs: 42 } })
    expect(wrapper.text()).toContain('1 resultado')
    expect(wrapper.text()).not.toContain('1 resultados')
    expect(wrapper.text()).toContain('42 ms')
  })

  it('renders plural label with multiple results', () => {
    const wrapper = mount(ResultBar, { props: { count: 7, tookMs: 120 } })
    expect(wrapper.text()).toContain('7 resultados')
    expect(wrapper.text()).toContain('120 ms')
  })

  it('omits tookMs span when null', () => {
    const wrapper = mount(ResultBar, { props: { count: 3, tookMs: null } })
    expect(wrapper.text()).toContain('3 resultados')
    expect(wrapper.text()).not.toContain('ms')
  })

  it('emits reset when the Nueva búsqueda button is clicked', async () => {
    const wrapper = mount(ResultBar, { props: { count: 2, tookMs: 50 } })
    const button = wrapper.find('button')
    expect(button.text()).toBe('Nueva búsqueda')
    await button.trigger('click')
    expect(wrapper.emitted('reset')).toHaveLength(1)
  })
})
