// ui_kits/web/PropertyCard.jsx — single listing card
// Source: frontend/src/components/PropertyCard.vue
// Kit additions (flagged): tipo badge inside the gradient header, staggered fade-up entrance.

const fmtPrice = (n) =>
  new Intl.NumberFormat('es-GT', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(n);

const fmtDate = (iso) =>
  new Intl.DateTimeFormat('es-GT', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date(iso + 'T00:00:00'));

const TIPO_LABEL = {
  casa: 'Casa',
  departamento: 'Departamento',
  terreno: 'Terreno',
  oficina: 'Oficina',
  local: 'Local',
};

const PropertyCard = ({ property: p }) => {
  const TipoIcon = TIPO_ICONS[p.tipo] ?? HouseIcon;
  const gradient = TIPO_GRADIENTS[p.tipo] ?? 'linear-gradient(135deg, #f3f4f6, #e5e7eb)';

  return (
    <article className="card prop-card" style={{ display: 'flex', flexDirection: 'column' }}>
      <div
        style={{
          aspectRatio: 'var(--kit-card-image-ratio, 16 / 10)',
          background: gradient,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'rgba(255,255,255,0.9)',
          position: 'relative',
        }}
      >
        {/* Tipo badge — kit addition */}
        <span style={{
          position: 'absolute',
          top: 12, left: 12,
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          padding: '4px 10px 4px 8px',
          borderRadius: 9999,
          background: 'rgba(255,255,255,0.92)',
          color: 'var(--neutral-800)',
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: '0.01em',
          backdropFilter: 'blur(4px)',
          WebkitBackdropFilter: 'blur(4px)',
          boxShadow: '0 1px 2px rgba(15,58,110,0.08)',
        }}>
          <span style={{ color: 'var(--neutral-500)' }}>
            <TipoIcon size={12} strokeWidth={2} />
          </span>
          {TIPO_LABEL[p.tipo] ?? p.tipo}
        </span>
        <TipoIcon size={64} strokeWidth={1.5} />
      </div>
      <div style={{
        padding: 'var(--kit-card-pad, 20px)',
        display: 'flex',
        flexDirection: 'column',
        gap: 10,
        flex: 1,
      }}>
        <header style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
          <h3 style={{
            fontSize: 'var(--fs-h2)',
            lineHeight: 1.2,
            fontWeight: 600,
            color: 'var(--neutral-900)',
            margin: 0,
            letterSpacing: '-0.005em',
          }}>{p.titulo}</h3>
          <p style={{
            fontSize: 'var(--fs-h2)',
            color: 'var(--primary-700)',
            whiteSpace: 'nowrap',
            fontWeight: 600,
            margin: 0,
            fontVariantNumeric: 'tabular-nums',
            letterSpacing: '-0.01em',
          }}>{fmtPrice(p.precio)}</p>
        </header>
        {p.descripcion && (
          <p style={{
            fontSize: 'var(--fs-body)',
            color: 'var(--neutral-600)',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            margin: 0,
            lineHeight: 1.45,
          }}>{p.descripcion}</p>
        )}
        <p style={{
          fontSize: 'var(--fs-caption)',
          color: 'var(--neutral-500)',
          display: 'flex',
          alignItems: 'center',
          gap: 4,
          margin: 0,
        }}>
          <MapPinIcon size={14} />
          {p.ubicacion}
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 'auto', paddingTop: 6 }}>
          {p.habitaciones != null && <span className="chip">{p.habitaciones} hab.</span>}
          {p.banos != null && <span className="chip">{p.banos} baños</span>}
          {p.area_m2 != null && <span className="chip">{p.area_m2} m²</span>}
        </div>
        <footer style={{ paddingTop: 10, borderTop: '1px solid var(--neutral-100)' }}>
          <p style={{ fontSize: 'var(--fs-caption)', color: 'var(--neutral-400)', margin: 0 }}>
            Publicado el {fmtDate(p.fecha_publicacion)}
          </p>
        </footer>
      </div>
    </article>
  );
};

const PropertyGrid = ({ properties }) => (
  <div className="prop-grid">
    {properties.map((p) => (
      <div key={p.id} className="prop-card-wrap">
        <PropertyCard property={p} />
      </div>
    ))}
  </div>
);

window.PropertyCard = PropertyCard;
window.PropertyGrid = PropertyGrid;
window.fmtPrice = fmtPrice;
window.fmtDate = fmtDate;
