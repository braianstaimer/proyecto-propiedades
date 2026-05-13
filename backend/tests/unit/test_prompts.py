from __future__ import annotations

from app.prompts import COLUMN_LIST, PROMPT_VERSION, PromptBuilder


def test_prompt_version_constant() -> None:
    assert PROMPT_VERSION == "v1"


def test_builder_inserts_user_query() -> None:
    builder = PromptBuilder()
    prompt = builder.build("Busco casas en zona 10")
    assert "Busco casas en zona 10" in prompt
    assert COLUMN_LIST in prompt


def test_builder_includes_few_shot_examples() -> None:
    builder = PromptBuilder()
    prompt = builder.build("any")
    for example in (
        "Busco casas de 3 habitaciones en zona 10",
        "departamentos de menos de",
        "Terrenos en venta con precio",
    ):
        assert example in prompt


def test_builder_includes_schema() -> None:
    builder = PromptBuilder()
    prompt = builder.build("any")
    for column in ("titulo", "precio", "habitaciones", "fecha_publicacion"):
        assert column in prompt


def test_retry_prompt_contains_error_reason() -> None:
    builder = PromptBuilder()
    retry = builder.build_retry("query x", "SQL_FORBIDDEN_TABLE")
    assert "SQL_FORBIDDEN_TABLE" in retry
    assert "query x" in retry


def test_builder_version_property() -> None:
    assert PromptBuilder().version == "v1"
