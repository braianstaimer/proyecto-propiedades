// ui_kits/web/AppHeader.jsx — sticky top header
// Source: frontend/src/components/AppHeader.vue

const AppHeader = ({ showSql, onToggleSql }) => (
  <header
    style={{
      position: 'sticky',
      top: 0,
      zIndex: 10,
      background: '#fff',
      borderBottom: '1px solid var(--neutral-200)',
    }}
  >
    <div
      style={{
        maxWidth: 'var(--container-max)',
        margin: '0 auto',
        padding: '16px 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 16,
      }}
    >
      <Logo />
      <button
        type="button"
        className="btn-secondary"
        aria-pressed={showSql}
        onClick={onToggleSql}
      >
        <ChevronsIcon size={16} />
        {showSql ? 'Ocultar SQL' : 'Mostrar SQL'}
      </button>
    </div>
  </header>
);

window.AppHeader = AppHeader;
