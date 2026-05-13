// ui_kits/web/SearchBar.jsx — hero search input + submit button
// Source: frontend/src/components/SearchBar.vue (placeholder rotation @ 4s)

const { useState, useEffect, useRef } = React;

const PLACEHOLDERS = [
  'Busco casas de 3 habitaciones en zona 10',
  'Muéstrame departamentos de menos de $150,000',
  'Propiedades con más de 2 baños y al menos 150 m²',
  'Casas publicadas en los últimos 30 días',
  'Terrenos entre $50,000 y $100,000',
];

const SearchBar = ({ value, onChange, onSubmit, loading }) => {
  const [phIndex, setPhIndex] = useState(0);
  const inputRef = useRef(null);

  useEffect(() => {
    const id = setInterval(() => setPhIndex((i) => (i + 1) % PLACEHOLDERS.length), 4000);
    return () => clearInterval(id);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!loading && value.trim()) onSubmit();
  };

  return (
    <form role="search" onSubmit={handleSubmit} style={{
      width: '100%',
      display: 'flex',
      gap: 12,
      flexDirection: 'row',
      flexWrap: 'wrap',
    }}>
      <label htmlFor="search-input" style={{ position: 'absolute', left: -9999 }}>Consulta</label>
      <div style={{ position: 'relative', flex: '1 1 360px' }}>
        <SearchIcon
          size={20}
          style={{
            position: 'absolute',
            left: 16,
            top: '50%',
            transform: 'translateY(-50%)',
            color: 'var(--neutral-400)',
          }}
        />
        <input
          id="search-input"
          ref={inputRef}
          type="search"
          className="input-search"
          value={value}
          placeholder={PLACEHOLDERS[phIndex]}
          disabled={loading}
          maxLength={500}
          autoComplete="off"
          spellCheck="true"
          onChange={(e) => onChange(e.target.value)}
          style={{ paddingLeft: 48 }}
        />
      </div>
      <button
        type="submit"
        className="btn-primary"
        disabled={loading || !value.trim()}
        aria-label="Buscar propiedades"
      >
        {loading ? (
          <>
            <SpinnerIcon size={16} className="spin" />
            Buscando…
          </>
        ) : 'Buscar'}
      </button>
    </form>
  );
};

window.SearchBar = SearchBar;
