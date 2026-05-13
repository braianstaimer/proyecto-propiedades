from __future__ import annotations

import pytest

from app.exceptions import (
    DatabaseError,
    DomainError,
    EmptyQueryError,
    LLMInvalidOutputError,
    LLMTimeoutError,
    LLMUnavailableError,
    RateLimitExceededError,
    SQLDangerousFunctionError,
    SQLForbiddenStatementError,
    SQLForbiddenTableError,
    SQLNotSelectError,
)


@pytest.mark.parametrize(
    "cls,code,status",
    [
        (EmptyQueryError, "EMPTY_QUERY", 422),
        (LLMTimeoutError, "LLM_TIMEOUT", 422),
        (LLMInvalidOutputError, "LLM_INVALID_OUTPUT", 422),
        (LLMUnavailableError, "LLM_UNAVAILABLE", 503),
        (SQLNotSelectError, "SQL_NOT_SELECT", 422),
        (SQLForbiddenTableError, "SQL_FORBIDDEN_TABLE", 422),
        (SQLForbiddenStatementError, "SQL_FORBIDDEN_STATEMENT", 422),
        (SQLDangerousFunctionError, "SQL_DANGEROUS_FUNCTION", 422),
        (DatabaseError, "DB_ERROR", 500),
        (RateLimitExceededError, "RATE_LIMIT", 429),
    ],
)
def test_exception_metadata(cls: type[DomainError], code: str, status: int) -> None:
    exc = cls()
    assert exc.code == code
    assert exc.http_status == status
    assert exc.message


def test_detail_propagates() -> None:
    err = EmptyQueryError("custom detail")
    assert err.detail == "custom detail"


def test_default_detail_is_none() -> None:
    err = EmptyQueryError()
    assert err.detail is None
