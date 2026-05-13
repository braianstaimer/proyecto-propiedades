USE propiedades_db;

INSERT IGNORE INTO propiedades
  (titulo, descripcion, tipo, precio, habitaciones, banos, area_m2, ubicacion, fecha_publicacion)
VALUES
  -- CASAS variadas
  ('Casa moderna en Zona 10',          'Acabados de lujo, jardin y parqueo doble.',     'casa',         320000.00, 3, 3, 240.00, 'Zona 10, Guatemala',         '2026-04-21'),
  ('Casa familiar en Zona 14',         '4 habitaciones, area social amplia.',           'casa',         410000.00, 4, 3, 285.50, 'Zona 14, Guatemala',         '2026-03-12'),
  ('Casa pequena en Zona 7',           'Ideal primera vivienda.',                       'casa',          95000.00, 2, 1,  90.00, 'Zona 7, Guatemala',          '2026-04-30'),
  ('Casa con jardin en Zona 16',       'Cantera de madera, acabados premium.',          'casa',         525000.00, 3, 3, 310.00, 'Zona 16, Guatemala',         '2026-05-02'),
  ('Casa estilo colonial Antigua',     'Patio central, ubicacion turistica.',           'casa',         280000.00, 3, 2, 200.00, 'Antigua Guatemala',          '2026-02-08'),

  -- DEPARTAMENTOS variados
  ('Apartamento en Zona 10',           'Edificio nuevo, vista panoramica.',             'departamento', 145000.00, 2, 2,  95.00, 'Zona 10, Guatemala',         '2026-04-25'),
  ('Apartamento economico Zona 11',    'Cerca de universidades.',                       'departamento',  78000.00, 1, 1,  55.00, 'Zona 11, Guatemala',         '2026-04-18'),
  ('Apartamento amplio Zona 14',       'Penthouse con terraza privada.',                'departamento', 295000.00, 3, 3, 180.00, 'Zona 14, Guatemala',         '2026-04-12'),
  ('Apartamento Zona 15',              'Ubicacion residencial tranquila.',              'departamento', 132000.00, 2, 2,  88.00, 'Zona 15, Guatemala',         '2026-04-29'),
  ('Apartamento Zona 15 Vista Hermosa','Acabados modernos, gimnasio en torre.',         'departamento', 168000.00, 2, 2, 102.00, 'Zona 15, Guatemala',         '2026-05-05'),
  ('Apartamento Zona 9',               'Centro comercial a 5 minutos.',                 'departamento', 118000.00, 2, 1,  72.00, 'Zona 9, Guatemala',          '2026-04-22'),

  -- TERRENOS
  ('Terreno Carretera a El Salvador',  'Plano, listo para construir.',                  'terreno',       65000.00, NULL, NULL, 600.00, 'Carretera a El Salvador',  '2026-03-20'),
  ('Terreno residencial Zona 16',      'Zona segura, escrituras al dia.',               'terreno',       89000.00, NULL, NULL, 480.00, 'Zona 16, Guatemala',       '2026-04-15'),
  ('Terreno comercial Zona 4',         'Ideal para edificio de oficinas.',              'terreno',      220000.00, NULL, NULL, 350.00, 'Zona 4, Guatemala',        '2026-04-02'),
  ('Terreno en Mixco',                 'Acceso pavimentado, todos los servicios.',      'terreno',       52000.00, NULL, NULL, 320.00, 'Mixco, Guatemala',         '2026-04-28'),

  -- OFICINAS Y LOCALES
  ('Oficina equipada Zona 10',         'Edificio corporativo, parqueo asignado.',       'oficina',      185000.00, NULL,    2, 120.00, 'Zona 10, Guatemala',      '2026-03-30'),
  ('Local comercial Zona 1',           'Historico, alto trafico peatonal.',             'local',        245000.00, NULL,    1, 150.00, 'Zona 1, Guatemala',       '2026-04-08'),
  ('Local en plaza Zona 13',           'Cerca del aeropuerto.',                         'local',        198000.00, NULL,    2, 110.00, 'Zona 13, Guatemala',      '2026-05-01'),

  -- CASAS RECIENTES (para cubrir "ultimos 30 dias" en demos)
  ('Casa de campo Atlantico',          'Vista al lago, ideal fin de semana.',           'casa',         175000.00, 3, 2, 220.00, 'Carretera al Atlantico',     '2026-05-08'),
  ('Casa moderna Zona 10 minimal',     'Diseno minimalista, smart home.',               'casa',         365000.00, 3, 3, 260.00, 'Zona 10, Guatemala',         '2026-05-10');
