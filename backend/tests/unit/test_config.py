from __future__ import annotations

from app.config import Settings, get_settings


def test_settings_defaults() -> None:
    s = get_settings()
    assert s.DB_BACKEND == "mysql"
    assert s.LLM_BACKEND in ("ollama", "mock")
    assert s.OLLAMA_MODEL == "llama3.2:3b"
    assert s.MAX_QUERY_LENGTH == 500
    assert s.DEFAULT_SQL_LIMIT == 50
    assert s.MAX_SQL_LIMIT == 200


def test_settings_dsn_format() -> None:
    s = Settings(DB_USER="u", DB_PASSWORD="p", DB_HOST="h", DB_PORT=3306, DB_NAME="db")
    dsn = s.mysql_dsn()
    assert dsn.startswith("mysql+aiomysql://u:p@h:3306/db")
    assert "charset=utf8mb4" in dsn


def test_settings_frozen() -> None:
    """Settings es immutable (Pydantic frozen)."""
    import pydantic
    s = get_settings()
    try:
        s.DB_HOST = "other"  # type: ignore[misc]
    except (pydantic.ValidationError, TypeError, AttributeError):
        return
    raise AssertionError("Settings should be frozen")


def test_get_settings_is_cached() -> None:
    a = get_settings()
    b = get_settings()
    assert a is b
