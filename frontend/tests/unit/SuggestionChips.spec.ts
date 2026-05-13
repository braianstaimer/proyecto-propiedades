import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SuggestionChips from '@/components/SuggestionChips.vue'

describe('SuggestionChips', () => {
  it('renders six suggestion buttons with hint and query', () => {
    const wrapper = mount(SuggestionChips)
    const buttons = wrapper.findAll('button')
    expect(buttons).toHaveLength(6)
    expect(wrapper.text()).toContain('Tipo + ubicación')
    expect(wrapper.text()).toContain('Casas de 3 habitaciones en zona 10')
    expect(wrapper.text()).toContain('Combinada')
    expect(wrapper.text()).toContain('Departamentos con 2 habitaciones en zona 15')
  })

  it('renders the section label', () => {
    const wrapper = mount(SuggestionChips)
    expect(wrapper.text()).toContain('Opciones sugeridas')
    expect(wrapper.text()).toContain('haga clic para probar')
  })

  it('emits pick with the matching query when a card is clicked', async () => {
    const wrapper = mount(SuggestionChips)
    const buttons = wrapper.findAll('button')
    await buttons[0].trigger('click')
    await buttons[3].trigger('click')

    const pickEvents = wrapper.emitted('pick')
    expect(pickEvents).toHaveLength(2)
    expect(pickEvents?.[0]).toEqual(['Casas de 3 habitaciones en zona 10'])
    expect(pickEvents?.[1]).toEqual(['Propiedades con más de 2 baños y 150 m²'])
  })
})
