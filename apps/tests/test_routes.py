from apps.main import app
import pytest_asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from db.models.base import Base
from db.models import User, Comment, Post
from unittest.mock import patch
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from apps.core.core_dependency.db_dependency import DBDependency
from fastapi import Depends
from apps.core.settings import *


TEST_DATABASE_URL = f"mysql+aiomysql://{settings.DB_SETTINGS.DB_USER}:{settings.DB_SETTINGS.DB_PASSWORD.get_secret_value()}" \
                    f"@{settings.DB_SETTINGS.DB_HOST}:{settings.DB_SETTINGS.DB_PORT}/{settings.DB_SETTINGS.DB_NAME}"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, autocommit=False)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def override_db():

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    def get_test_db():
        return TestSessionLocal

    app.dependency_overrides[DBDependency] = lambda: DBDependency()
    app.dependency_overrides[DBDependency().db_session] = get_test_db

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
def mock_send_email():
    with patch("apps.auth.tasks.send_confirmation_email.delay") as mock_task:
        yield mock_task


@pytest.mark.asyncio
async def test_auth_register(mock_send_email):
    data = {
        "email": "example@mail.ru",
        "password": "passwordLosh24598"
    }
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/api/v1/auth/register", json=data)

    assert response.status_code == 200
    result = response.json()
    assert result["email"] == data["email"]
    mock_send_email.assert_called_once()