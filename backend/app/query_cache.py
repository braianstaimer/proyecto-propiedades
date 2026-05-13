"""Cache LRU en memoria para `sanitized_query → ValidatedSQL`.

Acelera consultas repetidas evitando el roundtrip al LLM (≈1s p50). La DB se
sigue consultando en cada request — los datos siguen frescos. Sólo se cachean
éxitos del pipeline LLM + validator (los errores no llenan el cache).

Tamaño configurable via `Settings.QUERY_CACHE_SIZE`. Con 0 (o negativo) el
cache queda desactivado (every get devuelve None, put es no-op).
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from threading import Lock

from app.sql_validator import ValidatedSQL


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0


@dataclass
class QueryCache:
    """LRU cache `str → ValidatedSQL` thread-safe.

    El lock es defensivo: FastAPI corre en un único event loop por worker
    (operaciones de dict son atómicas en CPython), pero el lock cubre el caso
    de tests multi-threaded y futuros workers híbridos.
    """

    max_size: int
    _store: OrderedDict[str, ValidatedSQL] = field(default_factory=OrderedDict)
    _lock: Lock = field(default_factory=Lock)
    stats: CacheStats = field(default_factory=CacheStats)

    @property
    def enabled(self) -> bool:
        return self.max_size > 0

    def get(self, key: str) -> ValidatedSQL | None:
        if not self.enabled:
            self.stats.misses += 1
            return None
        with self._lock:
            value = self._store.get(key)
            if value is None:
                self.stats.misses += 1
                return None
            self._store.move_to_end(key)
            self.stats.hits += 1
            return value

    def put(self, key: str, value: ValidatedSQL) -> None:
        if not self.enabled:
            return
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
                self._store[key] = value
                return
            self._store[key] = value
            if len(self._store) > self.max_size:
                self._store.popitem(last=False)
                self.stats.evictions += 1

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
        self.stats = CacheStats()

    def __len__(self) -> int:
        return len(self._store)


__all__ = ["CacheStats", "QueryCache"]
