// ui_kits/web/SearchView.jsx — refined editorial composition with Tweaks support.
// Source: frontend/src/views/SearchView.vue + App.vue.
// Visual liberties (flagged in README):
//   - eyebrow pill above the headline
//   - subtle dotted-grid texture + brand-tinted radial glows in the hero band
//   - tipo badge inside the property card gradient header
//   - staggered fade-up entrance on result cards
//   - tweaks panel: brand emphasis, hero scale, density, show-SQL-on-load, headline copy

const { useState: useStateSV, useEffect: useEffectSV, useMemo: useMemoSV } = React;

// ---------- Tweaks ----------
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "brandEmphasis": "azul",
  "heroScale": "regular",
  "density": "comfy",
  "showSqlOnLoad": true,
  "headline": "Encuentre su próxima propiedad"
}/*EDITMODE-END*/;

// ---------- Hero ----------
const Hero = ({ scale, headline, brandEmphasis }) => {
  const sizes = {
    compact:   { fs: 36, lh: 1.1,  sub: 15, eyebrowMb: 14, headlineMb: 10, subMax: 520 },
    regular:   { fs: 52, lh: 1.05, sub: 17, eyebrowMb: 18, headlineMb: 14, subMax: 560 },
    editorial: { fs: 76, lh: 0.98, sub: 19, eyebrowMb: 22, headlineMb: 18, subMax: 620 },
  };
  const s = sizes[scale] ?? sizes.regular;
  const eyebrowColor = brandEmphasis === 'terracota' ? 'var(--accent-700)' : 'var(--primary-700)';
  const eyebrowBg    = brandEmphasis === 'terracota' ? 'var(--accent-50)'  : 'var(--primary-50)';
  const eyebrowBorder= brandEmphasis === 'terracota' ? 'var(--accent-200)' : 'var(--primary-200)';

  return (
    <section style={{ textAlign: 'center', marginBottom: 36 }}>
      <span style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
        padding: '6px 12px 6px 10px',
        borderRadius: 9999,
        background: eyebrowBg,
        border: `1px solid ${eyebrowBorder}`,
        color: eyebrowColor,
        fontSize: 12,
        fontWeight: 500,
        letterSpacing: '0.01em',
        marginBottom: s.eyebrowMb,
        whiteSpace: 'nowrap',
      }}>
        <span style={{
          width: 6, height: 6, borderRadius: 9999,
          background: eyebrowColor, boxShadow: `0 0 0 4px ${eyebrowBg}`,
        }} />
        Búsqueda con IA · LLM local + SQL validado
      </span>
      <h1 style={{
        fontSize: s.fs,
        lineHeight: s.lh,
        fontWeight: 700,
        letterSpacing: '-0.025em',
        color: 'var(--neutral-900)',
        margin: 0,
        marginBottom: s.headlineMb,
        textWrap: 'balance',
      }}>{headline}</h1>
      <p style={{
        fontSize: s.sub,
        color: 'var(--neutral-600)',
        maxWidth: s.subMax,
        margin: '0 auto',
        lineHeight: 1.55,
      }}>
        Escriba en español natural lo que busca. Traducimos su consulta a una búsqueda
        precisa sobre miles de propiedades — sin filtros, sin formularios.
      </p>
    </section>
  );
};

// ---------- Suggestions ----------
// Patrones que entiende el LLM, presentados como mini-cards.
// Los 6 ejemplos vienen del PDF (README del repo raíz).
const SUGGESTION_GROUPS = [
  { hint: 'Tipo + ubicación', query: 'Casas de 3 habitaciones en zona 10',         Icon: MapPinIcon },
  { hint: 'Precio máximo',   query: 'Departamentos de menos de $150,000',          Icon: TagIcon },
  { hint: 'Rango de precio',  query: 'Terrenos entre $50,000 y $100,000',           Icon: ArrowsLeftRightIcon },
  { hint: 'Características', query: 'Propiedades con más de 2 baños y 150 m²',    Icon: SlidersIcon },
  { hint: 'Fecha',            query: 'Casas publicadas en los últimos 30 días',     Icon: CalendarIcon },
  { hint: 'Combinada',        query: 'Departamentos con 2 habitaciones en zona 15', Icon: SparklesIcon },
];

const SuggestionChips = ({ onPick, brandEmphasis }) => {
  const tone = brandEmphasis === 'terracota' ? 'accent' : 'primary';
  return (
    <div className="suggestions">
      <div className="suggestions__head">
        <span className={`suggestions__label suggestions__label--${tone}`}>Opciones sugeridas</span>
        <span className="suggestions__hint">Patrones que entendemos · haga clic para probar</span>
      </div>
      <div className="suggestions__grid">
        {SUGGESTION_GROUPS.map((s) => (
          <button
            key={s.query}
            type="button"
            className="suggestion-card"
            onClick={() => onPick(s.query)}
          >
            <span className="suggestion-card__icon">
              <s.Icon size={16} strokeWidth={2} />
            </span>
            <span className="suggestion-card__body">
              <span className="suggestion-card__hint">{s.hint}</span>
              <span className="suggestion-card__query">{s.query}</span>
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};

// ---------- Result bar ----------
const ResultBar = ({ count, tookMs, onReset, brandEmphasis }) => {
  const dotColor = brandEmphasis === 'terracota' ? 'var(--accent-500)' : 'var(--primary-500)';
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      gap: 12, paddingBottom: 4,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          padding: '4px 12px 4px 10px',
          borderRadius: 9999,
          background: '#fff',
          border: '1px solid var(--neutral-200)',
          fontSize: 13, fontWeight: 600, color: 'var(--neutral-800)',
          whiteSpace: 'nowrap',
        }}>
          <span style={{
            width: 8, height: 8, borderRadius: 9999,
            background: dotColor,
            boxShadow: '0 0 0 3px rgba(17, 131, 237, 0.12)',
          }} />
          {count} {count === 1 ? 'resultado' : 'resultados'}
        </span>
        {tookMs != null && (
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 12, color: 'var(--neutral-500)',
            whiteSpace: 'nowrap',
          }}>{tookMs} ms</span>
        )}
      </div>
      <button type="button" className="btn-secondary" onClick={onReset}>
        Nueva búsqueda
      </button>
    </div>
  );
};

// ---------- App ----------
const App = () => {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);

  const [showSql, setShowSql] = useStateSV(t.showSqlOnLoad);
  const initialQuery = 'Casas en zona 10 con 3 habitaciones';
  const initialResp = mockSearch(initialQuery);
  const [query, setQuery] = useStateSV(initialQuery);
  const [loading, setLoading] = useStateSV(false);
  const [response, setResponse] = useStateSV(initialResp.ok ? {
    sql: initialResp.sql, results: initialResp.results,
    took_ms: initialResp.took_ms, count: initialResp.count,
  } : null);
  const [error, setError] = useStateSV(null);
  const [hasSearched, setHasSearched] = useStateSV(true);
  const [searchToken, setSearchToken] = useStateSV(0); // bumps to re-trigger entrance anim

  // Re-sync showSql when its tweak default changes
  useEffectSV(() => { setShowSql(t.showSqlOnLoad); }, [t.showSqlOnLoad]);

  // Apply density to the document via CSS custom properties
  useEffectSV(() => {
    const root = document.documentElement;
    if (t.density === 'compact') {
      root.style.setProperty('--kit-grid-gap', '16px');
      root.style.setProperty('--kit-card-pad', '14px');
      root.style.setProperty('--kit-card-image-ratio', '16 / 9');
    } else {
      root.style.setProperty('--kit-grid-gap', '24px');
      root.style.setProperty('--kit-card-pad', '20px');
      root.style.setProperty('--kit-card-image-ratio', '16 / 10');
    }
  }, [t.density]);

  // Apply brand emphasis (swap which color leads accents on header/eyebrow)
  useEffectSV(() => {
    document.documentElement.dataset.brand = t.brandEmphasis;
  }, [t.brandEmphasis]);

  const runSearch = (q) => {
    setLoading(true);
    setError(null);
    setHasSearched(true);
    setTimeout(() => {
      if (/\berror\b/i.test(q)) {
        setError({ code: 'LLM_TIMEOUT', message: 'El modelo no respondió a tiempo.' });
        setResponse(null);
        setLoading(false);
        setSearchToken((n) => n + 1);
        return;
      }
      const r = mockSearch(q);
      if (!r.ok) {
        setError({ code: r.error.code, message: r.error.message });
        setResponse(null);
      } else {
        setResponse({ sql: r.sql, results: r.results, took_ms: r.took_ms, count: r.count });
      }
      setLoading(false);
      setSearchToken((n) => n + 1);
    }, 900);
  };

  const handleSubmit = () => runSearch(query);
  const handleSuggestion = (s) => { setQuery(s); runSearch(s); };
  const handleReset = () => {
    setQuery(''); setResponse(null); setHasSearched(false); setError(null);
  };

  const isEmpty = hasSearched && !loading && !error && response?.results?.length === 0;
  const hasResults = hasSearched && !loading && !error && response?.results?.length > 0;

  return (
    <>
      <AppHeader showSql={showSql} onToggleSql={() => setShowSql((v) => !v)} brandEmphasis={t.brandEmphasis} />
      <div className="hero-band">
        <div className="hero-band-inner">
          <Hero scale={t.heroScale} headline={t.headline} brandEmphasis={t.brandEmphasis} />
          <section style={{ maxWidth: 960, margin: '0 auto' }}>
            <div style={{ maxWidth: 720, margin: '0 auto' }}>
              <SearchBar value={query} onChange={setQuery} onSubmit={handleSubmit} loading={loading} />
            </div>
            <SuggestionChips onPick={handleSuggestion} brandEmphasis={t.brandEmphasis} />
          </section>
        </div>
      </div>

      <main className="results-shell">
        {error && (
          <section style={{ maxWidth: 720, margin: '0 auto 32px' }}>
            <ErrorAlert code={error.code} message={error.message} onDismiss={() => setError(null)} />
          </section>
        )}

        {loading && <section aria-live="polite"><LoadingSkeleton /></section>}

        {isEmpty && <EmptyState query={query} />}

        {hasResults && (
          <section key={searchToken} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <ResultBar count={response.count} tookMs={response.took_ms} onReset={handleReset} brandEmphasis={t.brandEmphasis} />
            {showSql && response.sql && <SqlPreview sql={response.sql} tookMs={response.took_ms} />}
            <PropertyGrid properties={response.results} />
          </section>
        )}
      </main>

      <TweaksPanel title="Tweaks">
        <TweakSection label="Brand" />
        <TweakRadio
          label="Emphasis"
          value={t.brandEmphasis}
          options={['azul', 'terracota']}
          onChange={(v) => setTweak('brandEmphasis', v)}
        />
        <TweakSection label="Hero" />
        <TweakRadio
          label="Scale"
          value={t.heroScale}
          options={['compact', 'regular', 'editorial']}
          onChange={(v) => setTweak('heroScale', v)}
        />
        <TweakText
          label="Headline"
          value={t.headline}
          onChange={(v) => setTweak('headline', v)}
        />
        <TweakSection label="Layout" />
        <TweakRadio
          label="Density"
          value={t.density}
          options={['compact', 'comfy']}
          onChange={(v) => setTweak('density', v)}
        />
        <TweakToggle
          label="Show SQL on load"
          value={t.showSqlOnLoad}
          onChange={(v) => setTweak('showSqlOnLoad', v)}
        />
      </TweaksPanel>
    </>
  );
};

window.App = App;
window.Hero = Hero;
