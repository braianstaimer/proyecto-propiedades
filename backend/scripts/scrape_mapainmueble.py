"""Scraper de https://mapainmueble.com → tabla `propiedades`.

Lee `sitemap.xml`, extrae las URLs de `/propiedades/<id>`, parsea el JSON-LD
(`RealEstateListing`) de cada ficha y carga las filas nuevas en MySQL usando
los campos existentes del modelo (sin modificar el esquema).

Dedup: usamos el UNIQUE KEY `uq_titulo_ubicacion (titulo, ubicacion)` del schema.
Cacheamos las tuplas existentes en memoria para evitar fetchs redundantes.

Uso:
    python -m scripts.scrape_mapainmueble --limit 50           # primer ingest
    python -m scripts.scrape_mapainmueble --limit 200 --concurrency 8
    python -m scripts.scrape_mapainmueble --dry-run --limit 5  # sin escribir
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sys
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import httpx
from sqlalchemy import text

# Permitir `python scripts/scrape_mapainmueble.py` desde backend/
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings  # noqa: E402
from app.database import build_datasource  # noqa: E402

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

SITEMAP_URL = "https://mapainmueble.com/sitemap.xml"
PROPERTY_PATH_PREFIX = "/propiedades/"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

# Slug ID en /propiedades/<XYZ123>:
#   pos 0 → región (C/D)
#   pos 1 → operación (V=Venta, A=Alquiler)
#   pos 2 → tipo de inmueble
SLUG_TIPO_MAP: dict[str, str] = {
    "A": "departamento",
    "C": "casa",
    "T": "terreno",
    "O": "oficina",
    "L": "local",
    # "B" (bodega) no existe en el ENUM del schema → se descarta
}

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)

JSONLD_RE = re.compile(
    r'<script\s+type="application/ld\+json">(\{.*?\})</script>',
    re.DOTALL,
)
AREA_RE = re.compile(
    r"(\d{2,4}(?:[.,]\d{1,2})?)\s*(?:m2|mts|m²|metros\s*cuadrados)",
    re.IGNORECASE,
)
SLUG_RE = re.compile(r"/propiedades/([A-Z]{3}\d+)/?$")

TITLE_MAX = 180
LOCATION_MAX = 160
DESCRIPTION_MAX = 4_000  # cap defensivo para TEXT

logger = logging.getLogger("scraper")


# ---------------------------------------------------------------------------
# Modelos en memoria
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ScrapedProperty:
    titulo: str
    descripcion: str | None
    tipo: str
    precio: float
    habitaciones: int | None
    banos: int | None
    area_m2: float | None
    ubicacion: str
    fecha_publicacion: date
    source_url: str


# ---------------------------------------------------------------------------
# Sitemap
# ---------------------------------------------------------------------------


async def fetch_property_urls(client: httpx.AsyncClient) -> list[str]:
    logger.info("sitemap.fetch start url=%s", SITEMAP_URL)
    response = await client.get(SITEMAP_URL)
    response.raise_for_status()
    root = ET.fromstring(response.text)

    urls: list[str] = []
    for url_el in root.findall("sm:url", SITEMAP_NS):
        loc_el = url_el.find("sm:loc", SITEMAP_NS)
        if loc_el is None or not loc_el.text:
            continue
        loc = loc_el.text.strip()
        if PROPERTY_PATH_PREFIX in loc:
            urls.append(loc)
    logger.info("sitemap.fetch done total=%d properties=%d", len(root), len(urls))
    return urls


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _parse_tipo_from_slug(url: str) -> str | None:
    match = SLUG_RE.search(url)
    if not match:
        return None
    slug = match.group(1)
    if len(slug) < 3:
        return None
    return SLUG_TIPO_MAP.get(slug[2].upper())


def _parse_area_m2(*texts: str | None) -> float | None:
    for txt in texts:
        if not txt:
            continue
        match = AREA_RE.search(txt)
        if not match:
            continue
        raw = match.group(1).replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            continue
        if 5 <= value <= 100_000:  # filtro de cordura
            return round(value, 2)
    return None


def _parse_date_posted(value: str | None) -> date | None:
    if not value:
        return None
    # ISO 8601 con TZ; tomamos sólo la parte de fecha
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _parse_price(offers: object) -> float | None:
    if not isinstance(offers, dict):
        return None
    raw = offers.get("price")
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _parse_location(address: object) -> str | None:
    if not isinstance(address, dict):
        return None
    locality = address.get("addressLocality")
    if isinstance(locality, str) and locality.strip():
        return locality.strip()[:LOCATION_MAX]
    region = address.get("addressRegion")
    if isinstance(region, str) and region.strip():
        return region.strip()[:LOCATION_MAX]
    return None


def _optional_int(value: object) -> int | None:
    if value in (None, 0, "0", ""):
        return None
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def parse_property(html: str, url: str) -> ScrapedProperty | None:
    """Extrae los campos requeridos. Devuelve `None` si la ficha no es válida."""
    tipo = _parse_tipo_from_slug(url)
    if tipo is None:
        return None  # bodega u otros tipos fuera de nuestro ENUM

    listing: dict | None = None
    for match in JSONLD_RE.finditer(html):
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "RealEstateListing":
            listing = data
            break
    if listing is None:
        return None

    titulo = (listing.get("name") or "").strip()
    if not titulo:
        return None
    titulo = titulo[:TITLE_MAX]

    ubicacion = _parse_location(listing.get("address"))
    if not ubicacion:
        return None

    precio = _parse_price(listing.get("offers"))
    if precio is None or precio < 0:
        return None

    fecha = _parse_date_posted(listing.get("datePosted"))
    if fecha is None:
        return None

    descripcion = listing.get("description")
    if isinstance(descripcion, str):
        descripcion = descripcion.strip()[:DESCRIPTION_MAX] or None
    else:
        descripcion = None

    return ScrapedProperty(
        titulo=titulo,
        descripcion=descripcion,
        tipo=tipo,
        precio=round(precio, 2),
        habitaciones=_optional_int(listing.get("numberOfRooms")),
        banos=_optional_int(listing.get("numberOfBathroomsTotal")),
        area_m2=_parse_area_m2(descripcion, titulo),
        ubicacion=ubicacion,
        fecha_publicacion=fecha,
        source_url=url,
    )


# ---------------------------------------------------------------------------
# Persistencia
# ---------------------------------------------------------------------------


INSERT_SQL = text(
    """
    INSERT IGNORE INTO propiedades
        (titulo, descripcion, tipo, precio, habitaciones, banos,
         area_m2, ubicacion, fecha_publicacion)
    VALUES
        (:titulo, :descripcion, :tipo, :precio, :habitaciones, :banos,
         :area_m2, :ubicacion, :fecha_publicacion)
    """
)


async def load_existing_keys(datasource) -> set[tuple[str, str]]:
    """Cachea (titulo, ubicacion) ya cargados para skipear sin tocar DB."""
    async with datasource.session() as session:
        result = await session.execute(text("SELECT titulo, ubicacion FROM propiedades"))
        return {(row[0], row[1]) for row in result}


async def insert_batch(datasource, items: Iterable[ScrapedProperty]) -> int:
    rows = [
        {
            "titulo": p.titulo,
            "descripcion": p.descripcion,
            "tipo": p.tipo,
            "precio": p.precio,
            "habitaciones": p.habitaciones,
            "banos": p.banos,
            "area_m2": p.area_m2,
            "ubicacion": p.ubicacion,
            "fecha_publicacion": p.fecha_publicacion,
        }
        for p in items
    ]
    if not rows:
        return 0
    async with datasource.session() as session:
        result = await session.execute(INSERT_SQL, rows)
        await session.commit()
        return result.rowcount or 0


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


async def fetch_and_parse(
    client: httpx.AsyncClient,
    url: str,
    semaphore: asyncio.Semaphore,
    retries: int = 2,
) -> ScrapedProperty | None:
    async with semaphore:
        for attempt in range(retries + 1):
            try:
                response = await client.get(url)
                if response.status_code == 429:
                    await asyncio.sleep(2 ** attempt)
                    continue
                response.raise_for_status()
                return parse_property(response.text, url)
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                if attempt == retries:
                    logger.warning("fetch.failed url=%s err=%s", url, exc)
                    return None
                await asyncio.sleep(0.5 * (attempt + 1))
        return None


async def run(args: argparse.Namespace) -> int:
    settings = get_settings()
    datasource = build_datasource(settings)

    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xml"}
    timeout = httpx.Timeout(20.0, connect=10.0)
    limits = httpx.Limits(max_connections=args.concurrency * 2)

    inserted_total = 0
    fetched = 0
    skipped_existing = 0
    skipped_invalid = 0

    try:
        existing = await load_existing_keys(datasource)
        logger.info("dedup.cache rows=%d", len(existing))

        async with httpx.AsyncClient(
            headers=headers, timeout=timeout, limits=limits, follow_redirects=True
        ) as client:
            all_urls = await fetch_property_urls(client)
            if args.limit:
                all_urls = all_urls[: args.limit]
            logger.info("scrape.start urls=%d concurrency=%d", len(all_urls), args.concurrency)

            semaphore = asyncio.Semaphore(args.concurrency)
            tasks = [fetch_and_parse(client, url, semaphore) for url in all_urls]

            batch: list[ScrapedProperty] = []
            for coro in asyncio.as_completed(tasks):
                fetched += 1
                prop = await coro
                if prop is None:
                    skipped_invalid += 1
                    continue
                key = (prop.titulo, prop.ubicacion)
                if key in existing:
                    skipped_existing += 1
                    continue
                existing.add(key)
                batch.append(prop)

                if len(batch) >= args.batch_size:
                    if args.dry_run:
                        inserted_total += len(batch)
                    else:
                        inserted_total += await insert_batch(datasource, batch)
                    batch.clear()

                if fetched % 25 == 0:
                    logger.info(
                        "progress fetched=%d inserted=%d skipped_existing=%d skipped_invalid=%d",
                        fetched, inserted_total, skipped_existing, skipped_invalid,
                    )

            if batch:
                if args.dry_run:
                    inserted_total += len(batch)
                else:
                    inserted_total += await insert_batch(datasource, batch)
    finally:
        await datasource.close()

    logger.info(
        "scrape.done fetched=%d inserted=%d skipped_existing=%d skipped_invalid=%d dry_run=%s",
        fetched, inserted_total, skipped_existing, skipped_invalid, args.dry_run,
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scraper mapainmueble.com → MySQL")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Procesar como máximo N URLs del sitemap (default: todas)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=6,
        help="Fetchs HTTP en paralelo (default: 6, recomendado ≤ 10)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Filas por INSERT IGNORE (default: 50)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No escribe en MySQL; sólo cuenta lo que insertaría",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
