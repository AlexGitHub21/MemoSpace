from apps.main import app
import pytest_asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from db.models.base import Base
from db.models import User, Comment, Post
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from apps.core.core_dependency.db_dependency import DBDependency
from apps.core.settings import *
from apps.auth.handlers import AuthHandler


TEST_DATABASE_URL = f"mysql+aiomysql://{settings.DB_SETTINGS.DB_USER}:{settings.DB_SETTINGS.DB_PASSWORD.get_secret_value()}" \
                    f"@{settings.DB_SETTINGS.DB_HOST}:{settings.DB_SETTINGS.DB_PORT}/{settings.DB_SETTINGS.DB_NAME}"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, autocommit=False)


@pytest_asyncio.fixture
async def test_session() -> AsyncSession:
    async with TestSessionLocal() as session:  # TestSessionLocal — async_sessionmaker
        yield session


@pytest_asyncio.fixture(scope="function", autouse=True)
async def override_db():

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



    app.dependency_overrides[DBDependency] = lambda: DBDependency()
    app.dependency_overrides[DBDependency().db_session] = test_session

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


@pytest.mark.asyncio
async def test_auth_confirm_register(mock_send_email):
    data = {
        "email": "example@mail.ru",
        "password": "passwordLosh24598"
    }
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/api/v1/auth/register", json=data)
        assert response.status_code == 200

        _, kwargs = mock_send_email.call_args
        sent_email = kwargs["to_email"]
        token = kwargs["token"]

        assert sent_email == data["email"]
        assert isinstance(token, str)

        response_confirm = await ac.get(
            f"/api/v1/auth/register_confirm?token={token}"
        )

    assert response_confirm.status_code == 200
    assert response_confirm.json() == {"message": "Электронная почта подтверждена"}


@pytest.mark.asyncio
async def test_auth_login(test_session):
    email = "example@mail.ru"
    password = "passwordLosh24598"
    hash_password = await AuthHandler().get_password_hash(password)

    # async for session in override_db():
    test_user = User(email=email, hashed_password=hash_password)
    test_session.add(test_user)
    await test_session.commit()
    await test_session.refresh(test_user)

    mock_redis = AsyncMock()
    mock_redis.__aenter__.return_value = mock_redis
    mock_redis.__aexit__.return_value = None
    with patch("apps.core.core_dependency.redis_dependency.RedisDependency.get_client",
        return_value=mock_redis
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post(
                "/api/v1/auth/login",
                json={"email": email, "password": password})
    assert response.status_code == 200
    assert response.json() == {"message":"Вход успешен"}

    cookies = response.cookies
    auth_cookie = cookies.get("Authorization")

    assert auth_cookie is not None
    assert len(auth_cookie) > 10