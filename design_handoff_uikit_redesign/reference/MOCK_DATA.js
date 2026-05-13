// Mock data — mirrors frontend types/api.ts PropertyOut shape.
// Curated to exercise all five tipos + the six PDF queries' worth of variety.

const MOCK_PROPERTIES = [
  {
    id: 1,
    titulo: 'Casa moderna en zona 10',
    descripcion: 'Casa de dos niveles con jardín, parqueo techado y acabados de lujo.',
    tipo: 'casa',
    precio: 185000,
    habitaciones: 3,
    banos: 3,
    area_m2: 220,
    ubicacion: 'Zona 10, Guatemala',
    fecha_publicacion: '2026-04-22',
  },
  {
    id: 2,
    titulo: 'Casa familiar zona 10',
    descripcion: 'Tres habitaciones, dos baños completos, área de servicio independiente.',
    tipo: 'casa',
    precio: 165000,
    habitaciones: 3,
    banos: 2,
    area_m2: 180,
    ubicacion: 'Zona 10, Guatemala',
    fecha_publicacion: '2026-05-01',
  },
  {
    id: 3,
    titulo: 'Apartamento luminoso zona 15',
    descripcion: 'Piso 8 con balcón vista al volcán, cocina equipada, dos parqueos.',
    tipo: 'departamento',
    precio: 135000,
    habitaciones: 2,
    banos: 2,
    area_m2: 92,
    ubicacion: 'Zona 15, Guatemala',
    fecha_publicacion: '2026-04-28',
  },
  {
    id: 4,
    titulo: 'Departamento amueblado zona 14',
    descripcion: 'Amueblado, listo para habitar. Gimnasio y piscina en el edificio.',
    tipo: 'departamento',
    precio: 145000,
    habitaciones: 2,
    banos: 2,
    area_m2: 85,
    ubicacion: 'Zona 14, Guatemala',
    fecha_publicacion: '2026-05-04',
  },
  {
    id: 5,
    titulo: 'Apartamento económico zona 11',
    descripcion: 'Excelente primera inversión, edificio nuevo con seguridad 24/7.',
    tipo: 'departamento',
    precio: 89000,
    habitaciones: 1,
    banos: 1,
    area_m2: 54,
    ubicacion: 'Zona 11, Guatemala',
    fecha_publicacion: '2026-04-18',
  },
  {
    id: 6,
    titulo: 'Terreno plano en Mixco',
    descripcion: 'Listo para construir, agua y luz disponibles, calle asfaltada.',
    tipo: 'terreno',
    precio: 72000,
    habitaciones: null,
    banos: null,
    area_m2: 450,
    ubicacion: 'Mixco, Guatemala',
    fecha_publicacion: '2026-04-10',
  },
  {
    id: 7,
    titulo: 'Oficina premium zona 9',
    descripcion: 'Planta libre 120 m², dos parqueos, recepción compartida.',
    tipo: 'oficina',
    precio: 215000,
    habitaciones: null,
    banos: 2,
    area_m2: 120,
    ubicacion: 'Zona 9, Guatemala',
    fecha_publicacion: '2026-03-30',
  },
  {
    id: 8,
    titulo: 'Local comercial zona 1',
    descripcion: 'Esquina con alto tráfico, vidriera amplia, sótano para bodega.',
    tipo: 'local',
    precio: 195000,
    habitaciones: null,
    banos: 1,
    area_m2: 95,
    ubicacion: 'Zona 1, Guatemala',
    fecha_publicacion: '2026-05-02',
  },
  {
    id: 9,
    titulo: 'Casa con jardín amplio',
    descripcion: 'Cuatro habitaciones, sala de estar, comedor independiente, jardín 100 m².',
    tipo: 'casa',
    precio: 245000,
    habitaciones: 4,
    banos: 3,
    area_m2: 260,
    ubicacion: 'Carretera a El Salvador',
    fecha_publicacion: '2026-04-25',
  },
];

// Fake search "router" — naive keyword matching just for the kit demo.
function mockSearch(query) {
  const q = (query || '').toLowerCase();
  const startedAt = performance.now();

  if (!q.trim()) return { ok: false, error: { code: 'EMPTY_QUERY', message: 'Ingrese una consulta.' } };

  const tipoMatch = q.match(/(casa|casas|departamento|departamentos|apartamento|apartamentos|terreno|terrenos|oficina|oficinas|local|locales)/);
  let tipo = null;
  if (tipoMatch) {
    const base = tipoMatch[1].replace(/s$/, '');
    tipo = base === 'apartamento' ? 'departamento' : base;
  }

  const habMatch = q.match(/(\d+)\s*hab/);
  const habitaciones = habMatch ? Number(habMatch[1]) : null;

  const zonaMatch = q.match(/zona\s*(\d+)/);
  const zona = zonaMatch ? Number(zonaMatch[1]) : null;

  const priceMatch = q.match(/(?:menos de|hasta|bajo)\s*\$?\s*([\d,]+)/);
  const priceMax = priceMatch ? Number(priceMatch[1].replace(/,/g, '')) : null;

  let results = MOCK_PROPERTIES.filter((p) => {
    if (tipo && p.tipo !== tipo) return false;
    if (habitaciones != null && p.habitaciones !== habitaciones) return false;
    if (zona != null && !p.ubicacion.toLowerCase().includes(`zona ${zona}`)) return false;
    if (priceMax != null && p.precio > priceMax) return false;
    return true;
  });

  // Fallback so the demo never feels broken
  if (results.length === 0 && !tipo && !habitaciones && !zona && !priceMax) {
    results = MOCK_PROPERTIES.slice(0, 6);
  }

  // Build a plausible SQL string for SqlPreview
  const where = [];
  if (tipo) where.push(`tipo = '${tipo}'`);
  if (habitaciones != null) where.push(`habitaciones = ${habitaciones}`);
  if (zona != null) where.push(`ubicacion LIKE '%zona ${zona}%'`);
  if (priceMax != null) where.push(`precio <= ${priceMax}`);

  const sql = `SELECT id, titulo, precio, tipo, habitaciones, banos, area_m2, ubicacion, fecha_publicacion
FROM propiedades
${where.length ? 'WHERE ' + where.join(' AND ') + '\n' : ''}ORDER BY fecha_publicacion DESC
LIMIT 200;`;

  return {
    ok: true,
    query,
    sql,
    count: results.length,
    results,
    took_ms: Math.round(performance.now() - startedAt + 80 + Math.random() * 220),
  };
}

window.MOCK_PROPERTIES = MOCK_PROPERTIES;
window.mockSearch = mockSearch;
