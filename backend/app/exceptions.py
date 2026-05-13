from __future__ import annotations


class DomainError(Exception):
    code: str = "DOMAIN_ERROR"
    http_status: int = 500
    message: str = "Error interno."

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail or self.message)
        self.detail = detail


class EmptyQueryError(DomainError):
    code = "EMPTY_QUERY"
    http_status = 422
    message = "La consulta está vacía o excede la longitud máxima."


class LLMTimeoutError(DomainError):
    code = "LLM_TIMEOUT"
    http_status = 422
    message = "El modelo tardó más del tiempo permitido. Intente de nuevo."


class LLMInvalidOutputError(DomainError):
    code = "LLM_INVALID_OUTPUT"
    http_status = 422
    message = "La respuesta del modelo no pudo interpretarse como SQL."


class LLMUnavailableError(DomainError):
    code = "LLM_UNAVAILABLE"
    http_status = 503
    message = "El servicio de IA no está disponible. Reintente en unos segundos."


class SQLNotSelectError(DomainError):
    code = "SQL_NOT_SELECT"
    http_status = 422
    message = "La consulta generada no es un SELECT permitido."


class SQLForbiddenTableError(DomainError):
    code = "SQL_FORBIDDEN_TABLE"
    http_status = 422
    message = "La consulta referencia tablas no permitidas."


class SQLForbiddenStatementError(DomainError):
    code = "SQL_FORBIDDEN_STATEMENT"
    http_status = 422
    message = "La consulta contiene sentencias múltiples no permitidas."


class SQLDangerousFunctionError(DomainError):
    code = "SQL_DANGEROUS_FUNCTION"
    http_status = 422
    message = "La consulta usa funciones SQL no permitidas."


class DatabaseError(DomainError):
    code = "DB_ERROR"
    http_status = 500
    message = "Error al consultar la base de datos."


class RateLimitExceededError(DomainError):
    code = "RATE_LIMIT"
    http_status = 429
    message = "Demasiadas solicitudes. Intente más tarde."
