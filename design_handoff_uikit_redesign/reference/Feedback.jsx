// ui_kits/web/Feedback.jsx — ErrorAlert + EmptyState + LoadingSkeleton + SqlPreview

const ERROR_HINTS = {
  LLM_TIMEOUT: 'El modelo tardó demasiado. Reintente con una consulta más corta.',
  LLM_UNAVAILABLE: 'El servicio de IA no responde. Verifique que Ollama esté corriendo.',
  LLM_INVALID_OUTPUT: 'El modelo no generó un SQL válido. Reformule la consulta.',
  SQL_NOT_SELECT: 'La consulta generada no es de sólo lectura. Reformule.',
  SQL_FORBIDDEN_TABLE: 'La consulta intenta acceder a una tabla no permitida.',
  SQL_DANGEROUS_FUNCTION: 'La consulta usa funciones no permitidas.',
  EMPTY_QUERY: 'Ingrese una consulta entre 1 y 500 caracteres.',
  DB_ERROR: 'Error al consultar la base de datos. Reintente en unos segundos.',
  NETWORK_ERROR: 'No se pudo conectar con el servidor.',
  RATE_LIMIT: 'Demasiadas solicitudes. Espere un momento.',
};

const ErrorAlert = ({ code, message, onDismiss }) => (
  <div role="alert" style={{
    background: 'var(--accent-50)',
    borderLeft: '4px solid var(--accent-500)',
    borderRadius: 'var(--radius-lg)',
    padding: 16,
    display: 'flex',
    alignItems: 'flex-start',
    gap: 12,
  }}>
    <AlertCircleIcon size={20} style={{ color: 'var(--accent-600)', flexShrink: 0, marginTop: 2 }} />
    <div style={{ flex: 1 }}>
      <p style={{ fontSize: 'var(--fs-body)', fontWeight: 600, color: 'var(--accent-800)', margin: 0 }}>{message}</p>
      {ERROR_HINTS[code] && (
        <p style={{ fontSize: 'var(--fs-caption)', color: 'var(--accent-700)', marginTop: 4 }}>{ERROR_HINTS[code]}</p>
      )}
      <p style={{
        fontSize: 'var(--fs-caption)',
        color: 'var(--accent-600)',
        marginTop: 8,
        fontFamily: 'var(--font-mono)',
      }}>code: {code}</p>
    </div>
    {onDismiss && (
      <button type="button" aria-label="Cerrar"
        style={{ background: 'none', border: 0, color: 'var(--accent-700)', cursor: 'pointer', padding: 4 }}
        onClick={onDismiss}>
        <XIcon size={18} />
      </button>
    )}
  </div>
);

const EmptyState = ({ query }) => (
  <div className="card" style={{ padding: '48px 32px', textAlign: 'center', maxWidth: 640, margin: '0 auto' }}>
    <SearchIcon size={56} strokeWidth={1.5} style={{ color: 'var(--neutral-300)', margin: '0 auto 16px', display: 'block' }} />
    <h2 style={{ fontSize: 'var(--fs-h2)', fontWeight: 600, color: 'var(--neutral-900)', margin: 0 }}>Sin resultados</h2>
    <p style={{ fontSize: 'var(--fs-body)', color: 'var(--neutral-600)', marginTop: 8 }}>
      {query
        ? <>No encontramos propiedades para <strong style={{ color: 'var(--neutral-900)' }}>"{query}"</strong>.</>
        : <>No encontramos propiedades para esa búsqueda.</>}
    </p>
    <p style={{ fontSize: 'var(--fs-caption)', color: 'var(--neutral-500)', marginTop: 16 }}>
      Pruebe variando el tipo, la zona, el rango de precio o el número de habitaciones.
    </p>
  </div>
);

const LoadingSkeleton = () => (
  <div className="prop-grid" role="status" aria-label="Cargando resultados">
    {[0, 1, 2].map((i) => (
      <div key={i} className="card" style={{ overflow: 'hidden' }}>
        <div className="pulse" style={{ aspectRatio: '16 / 10', background: 'var(--neutral-100)' }} />
        <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div className="pulse" style={{ height: 20, background: 'var(--neutral-100)', borderRadius: 4, width: '75%' }} />
          <div className="pulse" style={{ height: 16, background: 'var(--neutral-100)', borderRadius: 4, width: '100%' }} />
          <div style={{ display: 'flex', gap: 8, paddingTop: 4 }}>
            <div className="pulse" style={{ height: 24, width: 64, background: 'var(--neutral-100)', borderRadius: 9999 }} />
            <div className="pulse" style={{ height: 24, width: 64, background: 'var(--neutral-100)', borderRadius: 9999 }} />
          </div>
        </div>
      </div>
    ))}
  </div>
);

const SqlPreview = ({ sql, tookMs }) => (
  <section
    className="card"
    style={{ background: 'var(--neutral-900)', borderColor: 'var(--neutral-800)', padding: 20 }}
    aria-label="SQL generado"
  >
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
      <h3 style={{
        fontSize: 'var(--fs-caption)',
        color: 'var(--neutral-400)',
        fontFamily: 'var(--font-mono)',
        textTransform: 'uppercase',
        letterSpacing: '0.1em',
        margin: 0,
        fontWeight: 400,
        whiteSpace: 'nowrap',
      }}>SQL generado</h3>
      {tookMs != null && (
        <span style={{ fontSize: 'var(--fs-caption)', color: 'var(--neutral-500)', fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap' }}>
          {tookMs} ms
        </span>
      )}
    </div>
    <pre style={{
      fontSize: 'var(--fs-caption)',
      fontFamily: 'var(--font-mono)',
      color: 'var(--primary-200)',
      whiteSpace: 'pre-wrap',
      wordBreak: 'break-all',
      margin: 0,
      lineHeight: 1.55,
    }}>{sql}</pre>
  </section>
);

Object.assign(window, { ErrorAlert, EmptyState, LoadingSkeleton, SqlPreview, ERROR_HINTS });
