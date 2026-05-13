from __future__ import annotations

import os

import pymysql
import pytest


def _db_kwargs() -> dict:
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", "3306")),
        "user": os.environ.get("MYSQL_ROOT_USER", "root"),
        "password": os.environ.get("MYSQL_ROOT_PASSWORD", "rootpass"),
        "database": os.environ.get("DB_NAME", "propiedades_db"),
        "connect_timeout": 2,
    }


@pytest.fixture
def sync_conn():
    try:
        conn = pymysql.connect(**_db_kwargs())
    except pymysql.MySQLError as exc:
        pytest.skip(f"MySQL no disponible: {exc}")
    try:
        yield conn
    finally:
        conn.close()


def test_table_exists_and_has_seed(sync_conn) -> None:
    with sync_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM propiedades")
        count = cur.fetchone()[0]
    assert count >= 15


def test_appuser_ro_only_has_select_grant(sync_conn) -> None:
    with sync_conn.cursor() as cur:
        cur.execute("SHOW GRANTS FOR 'appuser_ro'@'%'")
        grants = " ".join(r[0] for r in cur.fetchall()).upper()
    assert "SELECT" in grants
    assert "INSERT" not in grants
    assert "UPDATE" not in grants
    assert "DELETE" not in grants
    assert "DROP" not in grants


def test_indexes_present(sync_conn) -> None:
    with sync_conn.cursor() as cur:
        cur.execute(
            "SELECT INDEX_NAME FROM information_schema.statistics "
            "WHERE table_schema = DATABASE() AND table_name = 'propiedades'"
        )
        names = {r[0].lower() for r in cur.fetchall()}
    assert "primary" in names
    for expected in ("idx_tipo", "idx_precio", "idx_ubicacion", "idx_fecha_publicacion"):
        assert expected in names


def test_unique_constraint_present(sync_conn) -> None:
    with sync_conn.cursor() as cur:
        cur.execute(
            "SELECT INDEX_NAME FROM information_schema.statistics "
            "WHERE table_schema = DATABASE() AND table_name = 'propiedades' "
            "AND non_unique = 0"
        )
        unique_indexes = {r[0].lower() for r in cur.fetchall()}
    assert "uq_titulo_ubicacion" in unique_indexes


def test_tipo_enum_values(sync_conn) -> None:
    with sync_conn.cursor() as cur:
        cur.execute(
            "SELECT COLUMN_TYPE FROM information_schema.columns "
            "WHERE table_schema=DATABASE() AND table_name='propiedades' AND column_name='tipo'"
        )
        column_type = cur.fetchone()[0]
    for value in ("casa", "departamento", "terreno", "oficina", "local"):
        assert value in column_type
