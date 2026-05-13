import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Eyebrow from '@/components/Eyebrow.vue'

describe('Eyebrow', () => {
  it('renders the slot content as a pill', () => {
    const wrapper = mount(Eyebrow, {
      slots: { default: 'Búsqueda con IA' },
    })
    expect(wrapper.text()).toContain('Búsqueda con IA')
  })

  it('uses primary tone classes by default', () => {
    const wrapper = mount(Eyebrow, { slots: { default: 'x' } })
    const pill = wrapper.find('span')
    expect(pill.classes()).toContain('bg-primary-50')
    expect(pill.classes()).toContain('border-primary-200')
    expect(pill.classes()).toContain('text-primary-700')
  })

  it('switches to accent tone when prop is set', () => {
    const wrapper = mount(Eyebrow, {
      props: { tone: 'accent' },
      slots: { default: 'x' },
    })
    const pill = wrapper.find('span')
    expect(pill.classes()).toContain('bg-accent-50')
    expect(pill.classes()).toContain('border-accent-200')
    expect(pill.classes()).toContain('text-accent-700')
  })
})
