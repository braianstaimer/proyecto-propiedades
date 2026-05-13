# Scripts — `proyecto-propiedades`

## `scrape_mapainmueble.py`

Scraper del sitemap de [mapainmueble.com](https://mapainmueble.com/sitemap.xml). Descarga las fichas de `/propiedades/<id>`, parsea el JSON-LD (`schema.org/RealEstateListing`) y carga las filas nuevas en la tabla `propiedades` **sin modificar el modelo**.

### Cómo detecta lo que ya está cargado

Usamos la `UNIQUE KEY uq_titulo_ubicacion (titulo, ubicacion)` que ya existe en `01_schema.sql`. El flujo:

1. Al arrancar, el script carga en memoria todas las tuplas `(titulo, ubicacion)` existentes (1 sólo `SELECT`).
2. Cada ficha parseada se compara contra ese set → se descarta si ya existe.
3. Como segundo cinturón de seguridad, los inserts usan `INSERT IGNORE`: si hubo una inserción concurrente, MySQL descarta el duplicado en lugar de levantar `IntegrityError`.

> No se agregaron campos como `external_id` ni `source_url` a la tabla. La unicidad por `(titulo, ubicacion)` es suficiente para la primer iteración.

### Mapeo de campos

| Tabla `propiedades` | Fuente en la ficha de mapainmueble |
|---|---|
| `titulo` | `name` del JSON-LD (cap 180 chars) |
| `descripcion` | `description` del JSON-LD (cap 4 000 chars) |
| `tipo` | Letra 3 del slug del URL (`CVA9438` → `A` → `departamento`) |
| `precio` | `offers.price` (USD) |
| `habitaciones` | `numberOfRooms` (`0` → `NULL`) |
| `banos` | `numberOfBathroomsTotal` (`0` → `NULL`) |
| `area_m2` | Regex `\d+(\.\d+)?\s*(m2|mts|metros cuadrados)` sobre nombre + descripción |
| `ubicacion` | `address.addressLocality` (fallback `addressRegion`, cap 160 chars) |
| `fecha_publicacion` | `datePosted` (parte `YYYY-MM-DD`) |

**Mapeo de la letra 3 del slug → ENUM `tipo`:**

| Slug | ENUM |
|---|---|
| `A` | `departamento` |
| `C` | `casa` |
| `T` | `terreno` |
| `O` | `oficina` |
| `L` | `local` |
| `B` (bodega) | **descartado** (no existe en el ENUM del schema) |

### Pre-requisitos

- MySQL del proyecto corriendo (`docker compose up -d mysql backend`).
- Variables de DB en `.env` o en el entorno (el script reusa `app.config.Settings`).
- httpx ya está en `requirements.txt` — **no hay dependencias nuevas**.

### Uso

Desde la carpeta `backend/`:

```bash
# Activar venv del backend
source venv/bin/activate

# Dry-run rápido (5 fichas, no escribe en DB)
python -m scripts.scrape_mapainmueble --dry-run --limit 5

# Primer ingest "real" — 50 propiedades
python -m scripts.scrape_mapainmueble --limit 50

# Ingest grande con mayor paralelismo
python -m scripts.scrape_mapainmueble --limit 500 --concurrency 8 --batch-size 100

# Ingest completo del sitemap (≈ 5 000 fichas, varios minutos)
python -m scripts.scrape_mapainmueble --concurrency 8
```

Desde dentro del contenedor del backend:

```bash
docker compose exec backend python -m scripts.scrape_mapainmueble --limit 100
```

#### Flags

| Flag | Default | Descripción |
|---|---|---|
| `--limit N` | (todas) | Recortar a las primeras N URLs del sitemap |
| `--concurrency N` | 6 | Fetchs HTTP simultáneos (recomendado ≤ 10) |
| `--batch-size N` | 50 | Filas por `INSERT IGNORE` |
| `--dry-run` | `false` | No escribe en MySQL; sólo cuenta lo que insertaría |
| `--log-level` | `INFO` | `DEBUG \| INFO \| WARNING \| ERROR` |

### Salida esperada

```
INFO scraper sitemap.fetch start url=https://mapainmueble.com/sitemap.xml
INFO scraper sitemap.fetch done total=7059 properties=5000
INFO scraper dedup.cache rows=20
INFO scraper scrape.start urls=50 concurrency=6
INFO scraper progress fetched=25 inserted=24 skipped_existing=0 skipped_invalid=1
INFO scraper scrape.done fetched=50 inserted=47 skipped_existing=0 skipped_invalid=3 dry_run=False
```

`skipped_invalid` corresponde a fichas sin JSON-LD válido, sin precio o de tipo no soportado (p. ej. bodegas).

### Idempotencia

Correr el script dos veces seguidas con el mismo `--limit` insertará la primera vez y `skipped_existing` ≈ `fetched` la segunda. Ya cargados quedan tal cual; no se actualizan campos para no pisar las filas del seed (`02_seed_data.sql`).

---

## Búsquedas en lenguaje natural habilitadas por el nuevo data set

Las 6 búsquedas del PDF siguen funcionando con el seed original. Con la data de **mapainmueble** podemos validar muchas más combinaciones, porque el sitemap aporta:

- Cobertura amplia de zonas de Ciudad de Guatemala (Z. 1, 4, 7, 9, 10, 11, 13, 14, 15, 16) + Mixco, Antigua, Santa Catarina Pinula, San Lucas Sacatepéquez, Amatitlán, Villa Canales, San José Pinula, Carretera al Atlántico y Carretera a El Salvador.
- Las 5 categorías del ENUM con miles de fichas reales.
- Precios desde unos USD 30 k hasta varios millones.

Ejemplos de queries que **antes traían 0–1 fila** y ahora deberían traer varias:

### Por tipo + zona

- `"Apartamentos en venta en zona 14"`
- `"Apartamentos en venta en zona 16"`
- `"Apartamentos en alquiler en zona 10"`
- `"Casas en venta en zona 11 Mixco"`
- `"Casas en venta en Carretera a El Salvador"`
- `"Oficinas en zona 10"`
- `"Locales comerciales en zona 13"`

### Por rango de precio

- `"Apartamentos de menos de $100,000"`
- `"Casas entre $200,000 y $400,000"`
- `"Terrenos de menos de $80,000"`
- `"Propiedades de más de $500,000 en zona 14"`

### Por habitaciones / baños / área

- `"Apartamentos con 2 habitaciones y 2 baños"`
- `"Casas con más de 3 habitaciones y al menos 200 m²"`
- `"Apartamentos de hasta 80 m² en zona 11"`
- `"Casas con 4 habitaciones en Carretera a El Salvador"`

### Por fecha de publicación

- `"Propiedades publicadas en los últimos 7 días"`
- `"Apartamentos publicados este mes en zona 15"`
- `"Casas publicadas en los últimos 30 días en Mixco"`

### Por municipio fuera de Ciudad de Guatemala

- `"Casas en Antigua Guatemala"`
- `"Terrenos en San Lucas Sacatepéquez"`
- `"Apartamentos en Santa Catarina Pinula"`
- `"Locales en San José Pinula"`

### Combos avanzados

- `"Apartamentos de 2 habitaciones, 2 baños y menos de $150,000 en zona 16"`
- `"Casas de 4+ habitaciones en zona 14 publicadas el último mes"`
- `"Terrenos en venta de más de 500 m² fuera de la capital"`

> **Tip:** Después del ingest, correr `curl -s http://localhost:8000/api/health` para confirmar que la DB sigue saludable y luego pegar cualquiera de las queries de arriba al POST `/api/search`.

---

## Limitaciones de la primer iteración

- Mapainmueble usa Cloudflare; el `User-Agent` Safari va sin cookies. Si Cloudflare endurece la protección, agregar un cookie jar o `cloudscraper`.
- `area_m2` se infiere por regex (`\d+\s*m2`). Cuando la descripción no menciona área, queda `NULL` (válido por schema).
- Bodegas y multifamiliares (`B` y otros prefijos) se descartan porque no existen en el ENUM. Si se agregan al modelo, sólo hay que extender `SLUG_TIPO_MAP`.
- No se almacena el `source_url`. Para auditar la procedencia conviene hacerlo en una iteración futura (campo `source_url VARCHAR(255) NULL` + índice).
