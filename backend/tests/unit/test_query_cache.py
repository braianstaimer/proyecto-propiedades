"""Tests del LRU cache de consultas `sanitized_query → ValidatedSQL`."""

from __future__ import annotations

from app.query_cache import QueryCache
from app.sql_validator import ValidatedSQL


def _vsql(text: str) -> ValidatedSQL:
    return ValidatedSQL(sql=text)


def test_disabled_cache_never_stores() -> None:
    cache = QueryCache(max_size=0)
    cache.put("k", _vsql("SELECT 1"))
    assert cache.get("k") is None
    assert len(cache) == 0
    assert cache.enabled is False


def test_negative_max_size_disables_cache() -> None:
    cache = QueryCache(max_size=-1)
    cache.put("k", _vsql("SELECT 1"))
    assert cache.get("k") is None
    assert cache.enabled is False


def test_put_then_get_returns_same_value() -> None:
    cache = QueryCache(max_size=4)
    value = _vsql("SELECT * FROM propiedades LIMIT 1")
    cache.put("query A", value)
    assert cache.get("query A") is value


def test_miss_returns_none_and_increments_miss_counter() -> None:
    cache = QueryCache(max_size=4)
    assert cache.get("nope") is None
    assert cache.stats.misses == 1
    assert cache.stats.hits == 0


def test_hit_increments_hit_counter_and_does_not_evict() -> None:
    cache = QueryCache(max_size=2)
    cache.put("a", _vsql("SQL_A"))
    cache.put("b", _vsql("SQL_B"))
    assert cache.get("a") is not None
    assert cache.get("a") is not None
    assert cache.stats.hits == 2
    assert cache.stats.evictions == 0


def test_lru_eviction_at_max_size() -> None:
    cache = QueryCache(max_size=2)
    cache.put("a", _vsql("SQL_A"))
    cache.put("b", _vsql("SQL_B"))
    cache.put("c", _vsql("SQL_C"))  # evicts "a" (LRU)
    assert cache.get("a") is None
    assert cache.get("b") is not None
    assert cache.get("c") is not None
    assert cache.stats.evictions == 1


def test_get_promotes_recent_key_to_protect_from_eviction() -> None:
    cache = QueryCache(max_size=2)
    cache.put("a", _vsql("SQL_A"))
    cache.put("b", _vsql("SQL_B"))
    # `a` se vuelve más reciente que `b`
    assert cache.get("a") is not None
    cache.put("c", _vsql("SQL_C"))  # debería evictar "b", no "a"
    assert cache.get("a") is not None
    assert cache.get("b") is None
    assert cache.get("c") is not None


def test_put_existing_key_updates_value_and_refreshes_recency() -> None:
    cache = QueryCache(max_size=2)
    cache.put("a", _vsql("SQL_A_v1"))
    cache.put("b", _vsql("SQL_B"))
    cache.put("a", _vsql("SQL_A_v2"))
    cache.put("c", _vsql("SQL_C"))  # `a` es ahora la más reciente; `b` evictada
    got = cache.get("a")
    assert got is not None and got.sql == "SQL_A_v2"
    assert cache.get("b") is None
    assert cache.get("c") is not None


def test_clear_resets_store_and_stats() -> None:
    cache = QueryCache(max_size=4)
    cache.put("a", _vsql("SQL_A"))
    cache.get("a")
    cache.get("missing")
    assert cache.stats.hits == 1
    assert cache.stats.misses == 1
    cache.clear()
    assert len(cache) == 0
    assert cache.stats.hits == 0
    assert cache.stats.misses == 0
    assert cache.get("a") is None
