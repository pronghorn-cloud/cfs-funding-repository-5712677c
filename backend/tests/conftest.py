"""Shared test fixtures."""

import asyncio
import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings, get_settings
from app.database import Base, get_db
from app.main import create_app


def get_test_settings() -> Settings:
    return Settings(
        database_url="sqlite+aiosqlite:///./test.db",
        environment="test",
        jwt_secret_key="test-secret-key",
        debug=True,
    )


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app():
    test_app = create_app()
    test_app.dependency_overrides[get_settings] = get_test_settings
    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Generate test auth headers with a valid JWT."""
    from jose import jwt

    settings = get_test_settings()
    payload = {
        "sub": str(uuid.uuid4()),
        "email": "test@example.com",
        "display_name": "Test User",
        "role": "admin",
        "organization_id": None,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return {"Authorization": f"Bearer {token}"}
