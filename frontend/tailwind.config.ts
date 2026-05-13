import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./index.html', './src/**/*.{vue,ts,js}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f7ff',
          100: '#e0eefe',
          200: '#bcdcfd',
          300: '#7fbffb',
          400: '#3a9df6',
          500: '#1183ed',
          600: '#0866cb',
          700: '#0850a3',
          800: '#0b4585',
          900: '#0e3a6e',
          950: '#062148',
        },
        accent: {
          50: '#fdf5f0',
          100: '#fae6da',
          200: '#f4c9b1',
          300: '#eda181',
          400: '#e57755',
          500: '#dd5832',
          600: '#cc4324',
          700: '#a93420',
          800: '#882c20',
          900: '#6e261e',
        },
        neutral: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        display: ['2.25rem', { lineHeight: '2.75rem', fontWeight: '700' }],
        h1: ['1.75rem', { lineHeight: '2.25rem', fontWeight: '600' }],
        h2: ['1.375rem', { lineHeight: '1.875rem', fontWeight: '600' }],
        body: ['1rem', { lineHeight: '1.5rem' }],
        caption: ['0.8125rem', { lineHeight: '1.125rem' }],
      },
      borderRadius: {
        xl: '0.875rem',
        '2xl': '1.25rem',
      },
      boxShadow: {
        card: '0 1px 3px 0 rgb(15 58 110 / 0.08), 0 1px 2px -1px rgb(15 58 110 / 0.06)',
        'card-hover': '0 10px 25px -5px rgb(15 58 110 / 0.12), 0 8px 10px -6px rgb(15 58 110 / 0.08)',
      },
      opacity: {
        92: '0.92',
      },
    },
  },
  plugins: [],
}

export default config
