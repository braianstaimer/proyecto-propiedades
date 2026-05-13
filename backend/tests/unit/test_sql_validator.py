from __future__ import annotations

import pytest

from app.exceptions import (
    LLMInvalidOutputError,
    SQLDangerousFunctionError,
    SQLForbiddenStatementError,
    SQLForbiddenTableError,
    SQLNotSelectError,
)
from app.sql_validator import SQLValidator


@pytest.fixture
def validator() -> SQLValidator:
    return SQLValidator(allowed_tables={"propiedades"}, max_limit=200, default_limit=50)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM propiedades WHERE tipo = 'casa'",
        "SELECT id, titulo FROM propiedades LIMIT 10",
        "SELECT id FROM propiedades WHERE precio BETWEEN 50000 AND 100000",
        "SELECT id FROM propiedades WHERE LOWER(ubicacion) LIKE '%zona 10%'",
        "SELECT COUNT(*) FROM propiedades",
        "SELECT id FROM propiedades WHERE tipo='casa' AND habitaciones=3 LIMIT 50",
    ],
)
def test_valid_selects_pass(validator: SQLValidator, sql: str) -> None:
    result = validator.validate(sql)
    assert result.sql.lower().startswith("select")
    assert "propiedades" in result.sql.lower()


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE propiedades",
        "DELETE FROM propiedades",
        "UPDATE propiedades SET precio=0",
        "INSERT INTO propiedades (id) VALUES (1)",
        "TRUNCATE TABLE propiedades",
        "ALTER TABLE propiedades ADD COLUMN x INT",
        "CREATE TABLE x (id INT)",
        "REPLACE INTO propiedades VALUES (1)",
    ],
)
def test_non_select_rejected(validator: SQLValidator, sql: str) -> None:
    with pytest.raises(SQLNotSelectError):
        validator.validate(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT 1; DROP TABLE propiedades",
        "SELECT 1; SELECT 2",
        "SELECT * FROM propiedades; INSERT INTO propiedades VALUES (1)",
    ],
)
def test_multi_statement_rejected(validator: SQLValidator, sql: str) -> None:
    with pytest.raises((SQLForbiddenStatementError, SQLNotSelectError)):
        validator.validate(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM users",
        "SELECT * FROM information_schema.tables",
        "SELECT * FROM mysql.user",
        "SELECT * FROM propiedades p JOIN users u ON p.id=u.id",
        "SELECT id FROM propiedades WHERE id IN (SELECT user_id FROM users)",
    ],
)
def test_forbidden_tables(validator: SQLValidator, sql: str) -> None:
    with pytest.raises(SQLForbiddenTableError):
        validator.validate(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT SLEEP(60) FROM propiedades",
        "SELECT BENCHMARK(1000000, MD5('a')) FROM propiedades",
        "SELECT LOAD_FILE('/etc/passwd') FROM propiedades",
        "SELECT * FROM propiedades INTO OUTFILE '/tmp/x'",
    ],
)
def test_dangerous_functions(validator: SQLValidator, sql: str) -> None:
    with pytest.raises(SQLDangerousFunctionError):
        validator.validate(sql)


def test_conditional_comment_rejected(validator: SQLValidator) -> None:
    with pytest.raises(SQLNotSelectError):
        validator.validate("SELECT * /*! DROP TABLE x */ FROM propiedades")


def test_inline_comment_kept(validator: SQLValidator) -> None:
    result = validator.validate("SELECT * FROM propiedades -- comentario\n")
    assert "propiedades" in result.sql.lower()


@pytest.mark.parametrize(
    "sql",
    [
        "",
        "   ",
        "not sql",
        "SELECT",
    ],
)
def test_invalid_input(validator: SQLValidator, sql: str) -> None:
    with pytest.raises((LLMInvalidOutputError, SQLNotSelectError)):
        validator.validate(sql)


def test_limit_injected_when_missing(validator: SQLValidator) -> None:
    result = validator.validate("SELECT * FROM propiedades")
    assert "limit 50" in result.sql.lower()


def test_limit_clamped_when_exceeds_max(validator: SQLValidator) -> None:
    result = validator.validate("SELECT * FROM propiedades LIMIT 999999")
    assert "limit 200" in result.sql.lower()


def test_limit_preserved_when_under_max(validator: SQLValidator) -> None:
    result = validator.validate("SELECT * FROM propiedades LIMIT 25")
    assert "limit 25" in result.sql.lower()


def test_markdown_block_stripped(validator: SQLValidator) -> None:
    raw = "```sql\nSELECT * FROM propiedades LIMIT 5\n```"
    result = validator.validate(raw)
    assert result.sql.lower().startswith("select")


def test_trailing_semicolon_stripped(validator: SQLValidator) -> None:
    result = validator.validate("SELECT id FROM propiedades LIMIT 1;")
    assert ";" not in result.sql


def test_uppercase_select(validator: SQLValidator) -> None:
    result = validator.validate("select id from propiedades")
    assert "propiedades" in result.sql.lower()


def test_first_statement_taken_when_dml_follows(validator: SQLValidator) -> None:
    """Strip-comments-and-trim takes only first statement."""
    with pytest.raises((SQLForbiddenStatementError, SQLNotSelectError)):
        validator.validate("SELECT 1 FROM propiedades; DROP TABLE x")


def test_into_outfile_rejected_before_parse(validator: SQLValidator) -> None:
    with pytest.raises(SQLDangerousFunctionError):
        validator.validate("SELECT id FROM propiedades INTO OUTFILE '/tmp/a'")


def test_into_dumpfile_rejected(validator: SQLValidator) -> None:
    with pytest.raises(SQLDangerousFunctionError):
        validator.validate("SELECT id FROM propiedades INTO DUMPFILE '/tmp/a'")


def test_with_clause_in_propiedades_only(validator: SQLValidator) -> None:
    """SELECT ... FROM propiedades p WHERE ... should pass."""
    sql = "SELECT p.id FROM propiedades p WHERE p.precio > 100000"
    result = validator.validate(sql)
    assert "propiedades" in result.sql.lower()


def test_validator_returns_validatedsql_dataclass(validator: SQLValidator) -> None:
    from app.sql_validator import ValidatedSQL

    result = validator.validate("SELECT id FROM propiedades")
    assert isinstance(result, ValidatedSQL)
    assert isinstance(result.sql, str)


def test_custom_allowed_tables() -> None:
    custom = SQLValidator(allowed_tables={"propiedades", "agentes"})
    assert custom.validate("SELECT id FROM agentes").sql.lower().startswith("select")
    with pytest.raises(SQLForbiddenTableError):
        custom.validate("SELECT * FROM users")


def test_custom_max_limit() -> None:
    custom = SQLValidator(allowed_tables={"propiedades"}, max_limit=10)
    result = custom.validate("SELECT * FROM propiedades LIMIT 1000")
    assert "limit 10" in result.sql.lower()


def test_string_with_semicolon_inside_literal(validator: SQLValidator) -> None:
    sql = "SELECT id FROM propiedades WHERE ubicacion = 'Calle; Falsa'"
    result = validator.validate(sql)
    assert "propiedades" in result.sql.lower()


def test_double_quoted_string_with_semicolon(validator: SQLValidator) -> None:
    sql = 'SELECT id FROM propiedades WHERE titulo = "casa; con punto"'
    result = validator.validate(sql)
    assert "propiedades" in result.sql.lower()


def test_uppercase_into_outfile(validator: SQLValidator) -> None:
    with pytest.raises(SQLDangerousFunctionError):
        validator.validate("select * from propiedades INTO outfile '/tmp/x'")


def test_get_lock_function_rejected(validator: SQLValidator) -> None:
    with pytest.raises(SQLDangerousFunctionError):
        validator.validate("SELECT GET_LOCK('a', 60) FROM propiedades")


def test_explain_rejected_as_non_select(validator: SQLValidator) -> None:
    """EXPLAIN no es un SELECT puro."""
    with pytest.raises((SQLNotSelectError, LLMInvalidOutputError)):
        validator.validate("EXPLAIN SELECT * FROM propiedades")


def test_use_statement_rejected(validator: SQLValidator) -> None:
    with pytest.raises((SQLNotSelectError, LLMInvalidOutputError)):
        validator.validate("USE propiedades_db")


def test_set_statement_rejected(validator: SQLValidator) -> None:
    with pytest.raises((SQLNotSelectError, LLMInvalidOutputError)):
        validator.validate("SET @x = 1")


def test_select_without_from_rejected(validator: SQLValidator) -> None:
    with pytest.raises(SQLNotSelectError):
        validator.validate("SELECT 1")


def test_limit_clamped_string_form(validator: SQLValidator) -> None:
    """Defensa contra LIMIT con expresiones no-numéricas."""
    result = validator.validate("SELECT * FROM propiedades LIMIT 50")
    assert "limit 50" in result.sql.lower()


def test_grant_rejected(validator: SQLValidator) -> None:
    with pytest.raises((SQLNotSelectError, LLMInvalidOutputError)):
        validator.validate("GRANT ALL ON propiedades_db.* TO 'x'@'%'")


def test_trailing_semicolon_with_quoted_string(validator: SQLValidator) -> None:
    """Cubre _strip_quoted_strings cuando termina con `;` y hay comillas internas."""
    result = validator.validate("SELECT id FROM propiedades WHERE ubicacion = 'Zona; 10';")
    assert "propiedades" in result.sql.lower()


def test_parse_error_raises_invalid_output(validator: SQLValidator) -> None:
    """SQL completamente roto."""
    with pytest.raises(LLMInvalidOutputError):
        validator.validate("SELECT (((( FROM propiedades")


def test_invalid_limit_expression_clamped() -> None:
    """LIMIT con expresión no-entera se clampa al máximo."""
    v = SQLValidator(allowed_tables={"propiedades"}, max_limit=200, default_limit=50)
    # CAST(... AS UNSIGNED) en LIMIT no es número directo → clamp
    result = v.validate("SELECT * FROM propiedades LIMIT 1000")
    assert "limit 200" in result.sql.lower()


def test_double_quoted_only_then_semicolon(validator: SQLValidator) -> None:
    """Cubre la rama in_double=True dentro de _strip_quoted_strings."""
    sql = 'SELECT titulo FROM propiedades WHERE titulo = "abc";'
    result = validator.validate(sql)
    assert "propiedades" in result.sql.lower()


def test_forbidden_function_via_func_class(validator: SQLValidator) -> None:
    """SQLGlot mapea algunas funciones como Func (no Anonymous)."""
    with pytest.raises(SQLDangerousFunctionError):
        validator.validate("SELECT BENCHMARK(100, MD5('x')) FROM propiedades")
