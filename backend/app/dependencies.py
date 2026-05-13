from __future__ import annotations

from fastapi import Request

from app.config import Settings, get_settings
from app.database import DataSource
from app.llm_service import LLMProvider
from app.repositories import PropertyRepository
from app.search_service import SearchService
from app.sql_validator import SQLValidator


def get_app_settings() -> Settings:
    return get_settings()


def get_datasource(request: Request) -> DataSource:
    return request.app.state.datasource


def get_llm_provider(request: Request) -> LLMProvider:
    return request.app.state.llm


def get_property_repository(request: Request) -> PropertyRepository:
    return request.app.state.repo


def get_sql_validator(request: Request) -> SQLValidator:
    return request.app.state.validator


def get_search_service(request: Request) -> SearchService:
    return request.app.state.search_service
