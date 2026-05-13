from __future__ import annotations

import logging
import re
from pathlib import Path

from sqlalchemy import text

from app.database import DataSource

logger = logging.getLogger(__name__)

PERSISTENCIA_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = PERSISTENCIA_DIR / "01_schema.sql"
SEED_FILE = PERSISTENCIA_DIR / "02_seed_data.sql"
TABLE_NAME = "propiedades"
MIN_SEED_ROWS_DEFAULT = 15


async def run_migrations_if_needed(
    datasource: DataSource, *, min_seed_rows: int = MIN_SEED_ROWS_DEFAULT
) -> None:
    """Idempotente: si la tabla no existe, corre schema. Si la fila count < min, corre seed."""
    async with datasource.session() as session:
        if not await _table_exists(session):
            logger.info("migrations.schema.applying", extra={"file": SCHEMA_FILE.name})
            await _execute_file(session, SCHEMA_FILE)
            await session.commit()
            logger.info("migrations.schema.applied")
        else:
            logger.info("migrations.schema.skipped")

        count = await _count_rows(session)
        if count < min_seed_rows:
            logger.info("migrations.seed.applying", extra={"current": count})
            await _execute_file(session, SEED_FILE)
            await session.commit()
            new_count = await _count_rows(session)
            logger.info("migrations.seed.applied", extra={"rows": new_count})
        else:
            logger.info("migrations.seed.skipped", extra={"rows": count})


async def _table_exists(session) -> bool:
    result = await session.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = :name"
        ),
        {"name": TABLE_NAME},
    )
    return (result.scalar() or 0) > 0


async def _count_rows(session) -> int:
    result = await session.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
    return int(result.scalar() or 0)


async def _execute_file(session, path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Migration file missing: {path}")
    statements = _split_sql_statements(path.read_text(encoding="utf-8"))
    for stmt in statements:
        cleaned = stmt.strip()
        if cleaned and not cleaned.startswith("--"):
            await session.execute(text(cleaned))


def _split_sql_statements(sql: str) -> list[str]:
    """Divide por `;` ignorando los que estén dentro de strings literales."""
    sql_no_comments = re.sub(r"^\s*--.*$", "", sql, flags=re.MULTILINE)
    out: list[str] = []
    buf: list[str] = []
    in_single = False
    in_double = False
    for ch in sql_no_comments:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        if ch == ";" and not in_single and not in_double:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        out.append("".join(buf))
    return out
