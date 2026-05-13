import type { SidebarsConfig } from '@docusaurus/plugin-content-docs'

const sidebars: SidebarsConfig = {
  mainSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Flujos',
      items: ['flows/search-flow'],
    },
    {
      type: 'category',
      label: 'Arquitectura',
      items: ['architecture/error-codes'],
    },
    {
      type: 'category',
      label: 'Referencia',
      items: ['reference/health'],
    },
  ],
}

export default sidebars
