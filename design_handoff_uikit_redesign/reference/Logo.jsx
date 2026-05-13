// ui_kits/web/Logo.jsx — house glyph + wordmark lockup
// Sourced from frontend/src/components/AppHeader.vue

const Logo = ({ size = 36, withWordmark = true }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="var(--primary-700)"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M3 12 12 3l9 9" />
      <path d="M5 10v10h14V10" />
      <path d="M10 20v-5h4v5" />
    </svg>
    {withWordmark && (
      <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.1 }}>
        <p style={{
          fontSize: 'var(--fs-h2)',
          lineHeight: '1.15',
          fontWeight: 600,
          color: 'var(--neutral-900)',
          letterSpacing: '-0.005em',
        }}>proyecto-propiedades</p>
        <p style={{
          fontSize: 'var(--fs-caption)',
          color: 'var(--neutral-500)',
          marginTop: 2,
        }}>Búsqueda en lenguaje natural</p>
      </div>
    )}
  </div>
);

window.Logo = Logo;
