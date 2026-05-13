from __future__ import annotations

import re
from dataclasses import dataclass

import sqlglot
from sqlglot import exp

from app.exceptions import (
    LLMInvalidOutputError,
    SQLDangerousFunctionError,
    SQLForbiddenStatementError,
    SQLForbiddenTableError,
    SQLNotSelectError,
)

ALLOWED_TABLES_DEFAULT: frozenset[str] = frozenset({"propiedades"})
FORBIDDEN_FUNCTIONS_DEFAULT: frozenset[str] = frozenset(
    {"SLEEP", "BENCHMARK", "LOAD_FILE", "INTO OUTFILE", "INTO DUMPFILE", "GET_LOCK"}
)
DANGEROUS_STATEMENT_TYPES: tuple[type[exp.Expression], ...] = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.TruncateTable,
    exp.Create,
    exp.Command,
)
MIN_RAW_SQL_LENGTH: int = 7  # "SELECT "


@dataclass(frozen=True)
class ValidatedSQL:
    sql: str


class SQLValidator:
    def __init__(
        self,
        allowed_tables: frozenset[str] | set[str] = ALLOWED_TABLES_DEFAULT,
        *,
        max_limit: int = 200,
        default_limit: int = 50,
        forbidden_functions: frozenset[str] | set[str] = FORBIDDEN_FUNCTIONS_DEFAULT,
    ) -> None:
        self._allowed_tables = frozenset(t.lower() for t in allowed_tables)
        self._max_limit = max_limit
        self._default_limit = default_limit
        self._forbidden_functions = frozenset(f.upper() for f in forbidden_functions)

    def validate(self, sql: str) -> ValidatedSQL:
        cleaned = self._strip_markdown(sql)
        if len(cleaned) < MIN_RAW_SQL_LENGTH:
            raise LLMInvalidOutputError("SQL vacío o demasiado corto.")
        self._reject_dangerous_substrings(cleaned)
        statements = self._parse(cleaned.rstrip(";").strip() if self._has_trailing_only_semicolon(cleaned) else cleaned)
        self._reject_multi_statement(statements)
        select = self._require_single_select(statements[0])
        self._reject_forbidden_tables(select)
        self._reject_forbidden_functions(select)
        clamped = self._clamp_limit(select)
        return ValidatedSQL(sql=clamped)

    @staticmethod
    def _strip_markdown(sql: str) -> str:
        s = sql.strip()
        s = s.removeprefix("```sql").removeprefix("```SQL").removeprefix("```")
        s = s.removesuffix("```")
        return s.strip()

    @staticmethod
    def _has_trailing_only_semicolon(sql: str) -> bool:
        """True si el único `;` está al final (statement único sin multi)."""
        trimmed = sql.rstrip()
        if not trimmed.endswith(";"):
            return False
        body = trimmed[:-1]
        return ";" not in SQLValidator._strip_quoted_strings(body)

    @staticmethod
    def _strip_quoted_strings(s: str) -> str:
        out: list[str] = []
        in_single = False
        in_double = False
        for ch in s:
            if ch == "'" and not in_double:
                in_single = not in_single
                continue
            if ch == '"' and not in_single:
                in_double = not in_double
                continue
            if in_single or in_double:
                continue
            out.append(ch)
        return "".join(out)

    @staticmethod
    def _reject_dangerous_substrings(sql: str) -> None:
        # MySQL conditional comments execute hidden DDL/DML
        if re.search(r"/\*!\s*", sql):
            raise SQLNotSelectError("Comentarios condicionales /*! ... */ no permitidos.")
        upper = sql.upper()
        if "INTO OUTFILE" in upper or "INTO DUMPFILE" in upper:
            raise SQLDangerousFunctionError("INTO OUTFILE / INTO DUMPFILE no permitido.")

    @staticmethod
    def _parse(sql: str) -> list[exp.Expression]:
        try:
            parsed = sqlglot.parse(sql, read="mysql")
        except sqlglot.errors.ParseError as exc:
            raise LLMInvalidOutputError(str(exc)) from exc
        statements = [p for p in parsed if p is not None]
        if not statements:
            raise LLMInvalidOutputError("Parse vacío.")
        return statements

    @staticmethod
    def _reject_multi_statement(statements: list[exp.Expression]) -> None:
        if len(statements) > 1:
            raise SQLForbiddenStatementError(f"Se detectaron {len(statements)} sentencias.")

    @staticmethod
    def _require_single_select(stmt: exp.Expression) -> exp.Select:
        if isinstance(stmt, DANGEROUS_STATEMENT_TYPES):
            raise SQLNotSelectError(f"Sentencia no permitida: {type(stmt).__name__}.")
        if not isinstance(stmt, exp.Select):
            raise SQLNotSelectError(f"Se esperaba SELECT, se recibió {type(stmt).__name__}.")
        return stmt

    def _reject_forbidden_tables(self, select: exp.Select) -> None:
        tables = {t.name.lower() for t in select.find_all(exp.Table)}
        if not tables:
            raise SQLNotSelectError("SELECT sin FROM no permitido.")
        invalid = tables - self._allowed_tables
        if invalid:
            raise SQLForbiddenTableError(f"Tablas no permitidas: {sorted(invalid)}")

    def _reject_forbidden_functions(self, select: exp.Select) -> None:
        for func in select.find_all(exp.Func):
            name = (func.name or func.key or "").upper()
            if name in self._forbidden_functions:
                raise SQLDangerousFunctionError(f"Función no permitida: {name}")
        # sqlglot maps SLEEP/BENCHMARK as Anonymous; double-check by name attribute
        for anon in select.find_all(exp.Anonymous):
            name = (anon.name or "").upper()
            if name in self._forbidden_functions:
                raise SQLDangerousFunctionError(f"Función no permitida: {name}")

    def _clamp_limit(self, select: exp.Select) -> str:
        existing = select.args.get("limit")
        if existing is None:
            select = select.limit(self._default_limit)
        else:
            try:
                current = int(existing.expression.name)
            except (AttributeError, ValueError):
                current = self._max_limit + 1
            if current > self._max_limit:
                select = select.limit(self._max_limit)
        return select.sql(dialect="mysql")
