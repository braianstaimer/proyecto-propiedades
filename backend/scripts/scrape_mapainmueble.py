"""Scraper de https://mapainmueble.com → tabla `propiedades`.

Pipeline:
    Sitemap → filtro por slug → fetch HTML → parse JSON-LD → dedup → INSERT IGNORE

Diseño:
    - `SitemapClient`        — descubre URLs de fichas.
    - `RetryingFetcher`      — HTTP GET con backoff sobre 403/429/5xx + UTF-8 forzado.
    - `PropertyParser`       — HTML → `ScrapedProperty` (pure function-like).
    - `PropertiesRepository` — load (titulo, ubicacion) + INSERT IGNORE con diagnóstico.
    - `IngestPipeline`       — orquesta el flujo con concurrency bounded y stats.

Usar early returns; sin ifs anidados.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sys
import xml.etree.ElementTree as ET
from collections.abc import AsyncIterator, Iterable, Iterator
from dataclasses import dataclass, fields
from datetime import date
from pathlib import Path

import httpx
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings  # noqa: E402
from app.database import DataSource, build_datasource  # noqa: E402

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

SITEMAP_URL = "https://mapainmueble.com/sitemap.xml"
PROPERTY_PATH_PREFIX = "/propiedades/"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)

# Slug `/propiedades/<XYZ123>`:
#   pos 0 → región (C/D)
#   pos 1 → operación (V=Venta, A=Alquiler)
#   pos 2 → tipo de inmueble
SLUG_OPERATION_MAP: dict[str, str] = {"V": "venta", "A": "alquiler"}
SLUG_TIPO_MAP: dict[str, str] = {
    "A": "departamento",
    "C": "casa",
    "T": "terreno",
    "O": "oficina",
    "L": "local",
}

JSONLD_RE = re.compile(
    r'<script\s+type="application/ld\+json"[^>]*>(.*?)</script>',
    re.DOTALL,
)
AREA_RE = re.compile(
    r"(\d{2,4}(?:[.,]\d{1,2})?)\s*(?:m2|mts|m²|metros\s*cuadrados)",
    re.IGNORECASE,
)
SLUG_RE = re.compile(r"/propiedades/([A-Za-z]{3}\d+)/?$")

TITLE_MAX = 180
LOCATION_MAX = 160
DESCRIPTION_MAX = 4_000
AREA_MIN = 5.0
AREA_MAX = 100_000.0
PRICE_MIN = 0.01

RETRY_STATUSES = frozenset({403, 429, 500, 502, 503, 504})

logger = logging.getLogger("scraper")


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SlugInfo:
    operation: str  # "venta" | "alquiler"
    tipo: str       # ENUM `propiedades.tipo`


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


@dataclass(frozen=True, slots=True)
class ParseOutcome:
    """Resultado normalizado de un intento de scrape de una URL."""

    property: ScrapedProperty | None = None
    fetch_error: bool = False
    parse_error: bool = False


@dataclass
class IngestStats:
    fetched: int = 0
    inserted: int = 0
    skipped_existing: int = 0
    skipped_filtered: int = 0
    skipped_fetch_error: int = 0
    skipped_parse_error: int = 0
    db_insert_ignored: int = 0  # filas que MySQL silenció (race u otra UNIQUE collision)

    def as_dict(self) -> dict[str, int]:
        return {f.name: getattr(self, f.name) for f in fields(self)}


@dataclass(frozen=True)
class IngestConfig:
    limit: int | None = None
    concurrency: int = 6
    batch_size: int = 50
    dry_run: bool = False
    only_venta: bool = True
    max_pending_factor: int = 4
    progress_every: int = 25


# ---------------------------------------------------------------------------
# JSON-LD walking
# ---------------------------------------------------------------------------


def iter_jsonld_objects(data: object) -> Iterator[dict]:
    """Recorre listas, `@graph` arrays y objetos planos, emitiendo dicts."""
    if isinstance(data, list):
        for item in data:
            yield from iter_jsonld_objects(item)
        return
    if not isinstance(data, dict):
        return
    graph = data.get("@graph")
    if isinstance(graph, list):
        yield from iter_jsonld_objects(graph)
        return
    yield data


def type_matches(obj: dict, expected: str) -> bool:
    raw = obj.get("@type")
    if isinstance(raw, str):
        return raw == expected
    if isinstance(raw, list):
        return expected in raw
    return False


def find_real_estate_listing(html: str) -> dict | None:
    for match in JSONLD_RE.finditer(html):
        payload = _safe_json_loads(match.group(1).strip())
        listing = _first_listing(payload)
        if listing is not None:
            return listing
    return None


def _safe_json_loads(raw: str) -> object:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _first_listing(payload: object) -> dict | None:
    for obj in iter_jsonld_objects(payload):
        if type_matches(obj, "RealEstateListing"):
            return obj
    return None


# ---------------------------------------------------------------------------
# Field extractors (puros)
# ---------------------------------------------------------------------------


def parse_slug(url: str) -> SlugInfo | None:
    match = SLUG_RE.search(url)
    if not match:
        return None
    slug = match.group(1).upper()
    operation = SLUG_OPERATION_MAP.get(slug[1])
    tipo = SLUG_TIPO_MAP.get(slug[2])
    if operation is None or tipo is None:
        return None
    return SlugInfo(operation=operation, tipo=tipo)


def parse_price(offers: object) -> float | None:
    if not isinstance(offers, dict):
        return None
    raw = offers.get("price")
    if raw is None:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    if value < PRICE_MIN:
        return None
    return round(value, 2)


def parse_location(address: object) -> str | None:
    if not isinstance(address, dict):
        return None
    for key in ("addressLocality", "addressRegion"):
        value = address.get(key)
        if not isinstance(value, str):
            continue
        cleaned = value.strip()
        if cleaned:
            return cleaned[:LOCATION_MAX]
    return None


def parse_date_posted(value: object) -> date | None:
    if not isinstance(value, str) or len(value) < 10:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def parse_area_m2(*texts: str | None) -> float | None:
    for raw in _iter_area_candidates(texts):
        value = _parse_float(raw)
        if value is None:
            continue
        if AREA_MIN <= value <= AREA_MAX:
            return round(value, 2)
    return None


def _iter_area_candidates(texts: Iterable[str | None]) -> Iterator[str]:
    for txt in texts:
        if not txt:
            continue
        for match in AREA_RE.finditer(txt):
            yield match.group(1)


def _parse_float(raw: str) -> float | None:
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return None


def coerce_optional_int(value: object) -> int | None:
    if value in (None, 0, "0", ""):
        return None
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def truncate_title(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    return cleaned[:TITLE_MAX]


def truncate_description(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()[:DESCRIPTION_MAX]
    return cleaned or None


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


class PropertyParser:
    """HTML + SlugInfo → ScrapedProperty | None. Sin side effects."""

    def parse(self, html: str, slug: SlugInfo) -> ScrapedProperty | None:
        listing = find_real_estate_listing(html)
        if listing is None:
            return None

        titulo = truncate_title(listing.get("name"))
        ubicacion = parse_location(listing.get("address"))
        precio = parse_price(listing.get("offers"))
        fecha = parse_date_posted(listing.get("datePosted"))
        if titulo is None or ubicacion is None or precio is None or fecha is None:
            return None

        descripcion = truncate_description(listing.get("description"))
        return ScrapedProperty(
            titulo=titulo,
            descripcion=descripcion,
            tipo=slug.tipo,
            precio=precio,
            habitaciones=coerce_optional_int(listing.get("numberOfRooms")),
            banos=coerce_optional_int(listing.get("numberOfBathroomsTotal")),
            area_m2=parse_area_m2(descripcion, titulo),
            ubicacion=ubicacion,
            fecha_publicacion=fecha,
        )


# ---------------------------------------------------------------------------
# HTTP fetch con retries
# ---------------------------------------------------------------------------


class RetryingFetcher:
    """GET con backoff sobre 403/429/5xx + UTF-8 forzado en la respuesta."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        retries: int = 3,
        base_backoff: float = 0.5,
    ) -> None:
        self._client = client
        self._retries = retries
        self._base_backoff = base_backoff

    async def get_html(self, url: str) -> str | None:
        for attempt in range(self._retries + 1):
            text_or_none = await self._attempt(url, attempt)
            if text_or_none is not None:
                return text_or_none
            if attempt >= self._retries:
                return None
        return None

    async def _attempt(self, url: str, attempt: int) -> str | None:
        try:
            response = await self._client.get(url)
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            logger.debug("fetch.transport_error url=%s attempt=%d err=%s", url, attempt, exc)
            await self._sleep_linear(attempt)
            return None
        if response.status_code in RETRY_STATUSES:
            logger.debug(
                "fetch.retry_status url=%s status=%d attempt=%d",
                url, response.status_code, attempt,
            )
            await self._sleep_exponential(attempt)
            return None
        if not response.is_success:
            logger.warning("fetch.bad_status url=%s status=%d", url, response.status_code)
            return None
        response.encoding = "utf-8"  # defensivo contra Content-Type mal configurado
        return response.text

    async def _sleep_linear(self, attempt: int) -> None:
        await asyncio.sleep(self._base_backoff * (attempt + 1))

    async def _sleep_exponential(self, attempt: int) -> None:
        await asyncio.sleep(self._base_backoff * (2 ** attempt))


# ---------------------------------------------------------------------------
# Sitemap
# ---------------------------------------------------------------------------


class SitemapClient:
    def __init__(self, client: httpx.AsyncClient, url: str = SITEMAP_URL) -> None:
        self._client = client
        self._url = url

    async def fetch_property_urls(self) -> list[str]:
        logger.info("sitemap.fetch start url=%s", self._url)
        response = await self._client.get(self._url)
        response.raise_for_status()
        response.encoding = "utf-8"
        urls = list(self._extract_property_urls(response.text))
        logger.info("sitemap.fetch done properties=%d", len(urls))
        return urls

    @staticmethod
    def _extract_property_urls(xml_text: str) -> Iterator[str]:
        root = ET.fromstring(xml_text)
        for url_el in root.findall("sm:url", SITEMAP_NS):
            loc = (url_el.findtext("sm:loc", default="", namespaces=SITEMAP_NS) or "").strip()
            if PROPERTY_PATH_PREFIX in loc:
                yield loc


# ---------------------------------------------------------------------------
# Repositorio
# ---------------------------------------------------------------------------


_INSERT_SQL = text(
    """
    INSERT IGNORE INTO propiedades
        (titulo, descripcion, tipo, precio, habitaciones, banos,
         area_m2, ubicacion, fecha_publicacion)
    VALUES
        (:titulo, :descripcion, :tipo, :precio, :habitaciones, :banos,
         :area_m2, :ubicacion, :fecha_publicacion)
    """
)


@dataclass(frozen=True, slots=True)
class InsertResult:
    inserted: int
    ignored: int


class PropertiesRepository:
    def __init__(self, datasource: DataSource) -> None:
        self._datasource = datasource

    async def load_existing_keys(self) -> set[tuple[str, str]]:
        async with self._datasource.session() as session:
            result = await session.execute(text("SELECT titulo, ubicacion FROM propiedades"))
            return {(row[0], row[1]) for row in result}

    async def insert_batch(self, items: list[ScrapedProperty]) -> InsertResult:
        if not items:
            return InsertResult(inserted=0, ignored=0)
        rows = [self._row(p) for p in items]
        async with self._datasource.session() as session:
            inserted = await self._execute_insert(session, rows)
        ignored = len(rows) - inserted
        self._log_partial(inserted, ignored)
        return InsertResult(inserted=inserted, ignored=ignored)

    @staticmethod
    async def _execute_insert(session, rows: list[dict]) -> int:
        try:
            result = await session.execute(_INSERT_SQL, rows)
            await session.commit()
        except SQLAlchemyError as exc:
            await session.rollback()
            logger.error("insert.failed batch=%d err=%s", len(rows), exc)
            return 0
        return result.rowcount or 0

    @staticmethod
    def _log_partial(inserted: int, ignored: int) -> None:
        if ignored <= 0:
            return
        logger.info("insert.partial inserted=%d ignored=%d", inserted, ignored)

    @staticmethod
    def _row(p: ScrapedProperty) -> dict:
        return {
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


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


class IngestPipeline:
    def __init__(
        self,
        *,
        fetcher: RetryingFetcher,
        parser: PropertyParser,
        repository: PropertiesRepository,
        sitemap: SitemapClient,
        config: IngestConfig,
    ) -> None:
        self._fetcher = fetcher
        self._parser = parser
        self._repository = repository
        self._sitemap = sitemap
        self._config = config

    async def run(self) -> IngestStats:
        stats = IngestStats()
        existing = await self._repository.load_existing_keys()
        logger.info("dedup.cache rows=%d", len(existing))

        urls = self._limit_urls(await self._sitemap.fetch_property_urls())
        logger.info(
            "scrape.start urls=%d concurrency=%d only_venta=%s dry_run=%s",
            len(urls), self._config.concurrency, self._config.only_venta, self._config.dry_run,
        )

        await self._consume_outcomes(urls, existing, stats)
        logger.info("scrape.done %s", stats.as_dict())
        return stats

    def _limit_urls(self, urls: list[str]) -> list[str]:
        if self._config.limit is None:
            return urls
        return urls[: self._config.limit]

    async def _consume_outcomes(
        self,
        urls: list[str],
        existing: set[tuple[str, str]],
        stats: IngestStats,
    ) -> None:
        batch: list[ScrapedProperty] = []
        async for outcome in self._stream_outcomes(urls, stats):
            stats.fetched += 1
            self._handle_outcome(outcome, batch, existing, stats)
            await self._maybe_flush(batch, stats)
            self._maybe_log_progress(stats)
        await self._flush(batch, stats)

    def _handle_outcome(
        self,
        outcome: ParseOutcome,
        batch: list[ScrapedProperty],
        existing: set[tuple[str, str]],
        stats: IngestStats,
    ) -> None:
        if outcome.fetch_error:
            stats.skipped_fetch_error += 1
            return
        if outcome.property is None:
            stats.skipped_parse_error += 1
            return
        key = (outcome.property.titulo, outcome.property.ubicacion)
        if key in existing:
            stats.skipped_existing += 1
            return
        existing.add(key)
        batch.append(outcome.property)

    async def _maybe_flush(self, batch: list[ScrapedProperty], stats: IngestStats) -> None:
        if len(batch) < self._config.batch_size:
            return
        await self._flush(batch, stats)

    async def _flush(self, batch: list[ScrapedProperty], stats: IngestStats) -> None:
        if not batch:
            return
        if self._config.dry_run:
            stats.inserted += len(batch)
            batch.clear()
            return
        result = await self._repository.insert_batch(batch)
        stats.inserted += result.inserted
        stats.db_insert_ignored += result.ignored
        batch.clear()

    def _maybe_log_progress(self, stats: IngestStats) -> None:
        every = self._config.progress_every
        if every <= 0 or stats.fetched % every != 0:
            return
        logger.info("progress %s", stats.as_dict())

    async def _stream_outcomes(
        self,
        urls: list[str],
        stats: IngestStats,
    ) -> AsyncIterator[ParseOutcome]:
        semaphore = asyncio.Semaphore(self._config.concurrency)
        max_pending = self._config.concurrency * self._config.max_pending_factor
        pending: set[asyncio.Task[ParseOutcome]] = set()

        for url in urls:
            slug = parse_slug(url)
            if not self._should_ingest(slug):
                stats.skipped_filtered += 1
                continue
            async for outcome in self._drain_if_full(pending, max_pending):
                yield outcome
            pending.add(asyncio.create_task(self._scrape_one(url, slug, semaphore)))

        while pending:
            async for outcome in self._drain_one(pending):
                yield outcome

    def _should_ingest(self, slug: SlugInfo | None) -> bool:
        if slug is None:
            return False
        if self._config.only_venta and slug.operation != "venta":
            return False
        return True

    async def _drain_if_full(
        self,
        pending: set[asyncio.Task[ParseOutcome]],
        max_pending: int,
    ) -> AsyncIterator[ParseOutcome]:
        if len(pending) < max_pending:
            return
        async for outcome in self._drain_one(pending):
            yield outcome

    @staticmethod
    async def _drain_one(
        pending: set[asyncio.Task[ParseOutcome]],
    ) -> AsyncIterator[ParseOutcome]:
        done, _ = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            pending.discard(task)
            yield task.result()

    async def _scrape_one(
        self,
        url: str,
        slug: SlugInfo,
        semaphore: asyncio.Semaphore,
    ) -> ParseOutcome:
        async with semaphore:
            html = await self._fetcher.get_html(url)
        if html is None:
            return ParseOutcome(fetch_error=True)
        prop = self._safe_parse(html, slug, url)
        if prop is None:
            return ParseOutcome(parse_error=True)
        return ParseOutcome(property=prop)

    def _safe_parse(self, html: str, slug: SlugInfo, url: str) -> ScrapedProperty | None:
        try:
            return self._parser.parse(html, slug)
        except Exception:  # noqa: BLE001 — última red de seguridad en el pipeline
            logger.exception("parse.unexpected_error url=%s", url)
            return None


# ---------------------------------------------------------------------------
# Wiring + CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scraper mapainmueble.com → MySQL")
    parser.add_argument("--limit", type=int, default=None,
                        help="Máximo de URLs del sitemap a procesar (default: todas)")
    parser.add_argument("--concurrency", type=int, default=6,
                        help="Fetchs HTTP simultáneos (default: 6)")
    parser.add_argument("--batch-size", type=int, default=50,
                        help="Filas por INSERT IGNORE (default: 50)")
    parser.add_argument("--dry-run", action="store_true",
                        help="No escribe en MySQL")
    parser.add_argument("--include-alquiler", action="store_true",
                        help="Incluir alquileres. Por defecto sólo se ingestan VENTAS "
                             "para no mezclar precios mensuales con precios de venta.")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser


def config_from_args(args: argparse.Namespace) -> IngestConfig:
    return IngestConfig(
        limit=args.limit,
        concurrency=args.concurrency,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        only_venta=not args.include_alquiler,
    )


async def execute(config: IngestConfig) -> IngestStats:
    settings = get_settings()
    datasource = build_datasource(settings)
    try:
        return await _run_with_datasource(datasource, config)
    finally:
        await datasource.close()


async def _run_with_datasource(datasource: DataSource, config: IngestConfig) -> IngestStats:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xml"}
    timeout = httpx.Timeout(20.0, connect=10.0)
    limits = httpx.Limits(max_connections=config.concurrency * 2)
    async with httpx.AsyncClient(
        headers=headers, timeout=timeout, limits=limits, follow_redirects=True,
    ) as client:
        pipeline = IngestPipeline(
            fetcher=RetryingFetcher(client),
            parser=PropertyParser(),
            repository=PropertiesRepository(datasource),
            sitemap=SitemapClient(client),
            config=config,
        )
        return await pipeline.run()


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    asyncio.run(execute(config_from_args(args)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
