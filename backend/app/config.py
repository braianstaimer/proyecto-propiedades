from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )

    # Database
    DB_BACKEND: Literal["mysql"] = "mysql"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "appuser"
    DB_PASSWORD: str = "apppass"
    DB_NAME: str = "propiedades_db"
    DB_POOL_SIZE: int = 5
    DB_POOL_RECYCLE_SECONDS: int = 1800

    # LLM
    LLM_BACKEND: Literal["ollama", "mock"] = "ollama"
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_TIMEOUT_SECONDS: int = 15
    MOCK_LLM: bool = False

    # API
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: ["http://localhost:8080", "http://localhost:5173"]
    )

    # Rate limiting (opt-in)
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 10

    # Search
    MAX_QUERY_LENGTH: int = 500
    MAX_SQL_LIMIT: int = 200
    DEFAULT_SQL_LIMIT: int = 50
    MIN_SEED_ROWS: int = 15
    # Cache de consultas (LRU en memoria). 0 desactiva el cache.
    # Caches el par sanitized_query → ValidatedSQL para evitar la llamada al
    # LLM en consultas repetidas. La DB se consulta siempre (datos frescos).
    QUERY_CACHE_SIZE: int = 256

    def mysql_dsn(self) -> str:
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
