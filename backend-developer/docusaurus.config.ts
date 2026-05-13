import { themes as prismThemes } from 'prism-react-renderer'
import type { Config } from '@docusaurus/types'
import type * as Preset from '@docusaurus/preset-classic'

const config: Config = {
  title: 'proyecto-propiedades · API Docs',
  tagline: 'Búsqueda de propiedades inmobiliarias en lenguaje natural',
  favicon: 'img/favicon.svg',

  url: process.env.DOCS_URL || 'http://localhost:3001',
  baseUrl: process.env.DOCS_BASE_URL || '/',
  organizationName: 'braianstaimer',
  projectName: 'proyecto-propiedades-backend-developer',

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'es',
    locales: ['es'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    [
      '@scalar/docusaurus',
      {
        label: 'API Reference',
        route: '/api-reference',
        configuration: {
          spec: { url: `${process.env.DOCS_BASE_URL || '/'}openapi.json` },
          hideClientButton: false,
          theme: 'default',
        },
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'proyecto-propiedades',
      logo: {
        alt: 'proyecto-propiedades',
        src: 'img/favicon.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'mainSidebar',
          position: 'left',
          label: 'Guías',
        },
        { to: '/api-reference', label: 'API Reference', position: 'left' },
        {
          href: 'https://github.com/braianstaimer/proyecto-propiedades-backend',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentación',
          items: [
            { label: 'Quickstart', to: '/intro' },
            { label: 'Flujo de búsqueda', to: '/flows/search-flow' },
            { label: 'Catálogo de errores', to: '/architecture/error-codes' },
          ],
        },
        {
          title: 'Repositorios',
          items: [
            { label: 'Backend', href: 'https://github.com/braianstaimer/proyecto-propiedades-backend' },
            { label: 'Frontend', href: 'https://github.com/braianstaimer/proyecto-propiedades-frontend' },
            { label: 'Esta documentación', href: 'https://github.com/braianstaimer/proyecto-propiedades-backend-developer' },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} proyecto-propiedades.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'json', 'sql', 'python'],
    },
  } satisfies Preset.ThemeConfig,
}

export default config
