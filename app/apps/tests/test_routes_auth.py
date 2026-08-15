from app.apps.main import app
import pytest_asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from app.db.models.base import Base
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.apps.core.core_dependency.dependencies import get_session
from app.apps.core.settings import db_settings


TEST_DATABASE_URL = f"mysql+aiomysql://{db_settings.DB_USER}:{db_settings.DB_PASSWORD.get_secret_value()}" \
                    f"@{db_settings.DB_HOST}:{db_settings.DB_PORT}/{db_settings.DB_NAME}"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, autocommit=False)


@pytest_asyncio.fixture
async def test_session():
    async with TestSessionLocal() as session:
        yield session


async def override_get_session():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function", autouse=True)
async def override_db():

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.dependency_overrides[get_session] = override_get_session

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(autouse=True)
def mock_send_email():
    with patch("app.apps.auth.tasks.send_confirmation_email.delay") as mock_task:
        yield mock_task


@pytest_asyncio.fixture(autouse=True)
async def mock_redis():
    mock_redis = AsyncMock()
    mock_redis.__aenter__.return_value = mock_redis
    mock_redis.__aexit__.return_value = None
    with patch("app.apps.core.core_dependency.redis_dependency.RedisDependency.get_client",
               return_value=mock_redis
    ):
        yield mock_redis


#Фикстура для отправки асинхронных HTTP-запросов непосредственно к FastAPI-приложению без запуска сервера.
@pytest_asyncio.fixture(autouse=True)
async def open_async_client():
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as open_async_client:
        yield open_async_client


@pytest_asyncio.fixture
async def register_user(open_async_client):
    data = {
        "email": "example@mail.ru",
        "password": "passwordLosh24598"
    }
    response = await open_async_client.post("/api/v1/auth/register", json=data)
    yield data, response


@pytest.mark.asyncio
async def test_auth_registration(open_async_client, register_user, mock_send_email):
    data, response = register_user

    assert response.status_code == 200
    result = response.json()
    assert result["email"] == data["email"]
    mock_send_email.assert_called_once()


@pytest.mark.asyncio
async def test_auth_register_confirm(open_async_client, register_user, mock_send_email):
    data, response = register_user
    assert response.status_code == 200

    _, kwargs = mock_send_email.call_args
    sent_email = kwargs["to_email"]
    token = kwargs["token"]

    assert sent_email == data["email"]
    assert isinstance(token, str)

    response_confirm = await open_async_client.get(
        f"/api/v1/auth/register_confirm?token={token}"
    )

    assert response_confirm.status_code == 200
    assert response_confirm.json() == {"message": "Электронная почта подтверждена"}


@pytest.mark.asyncio
async def test_auth_login(open_async_client, register_user, mock_redis, test_session):

    data, response = register_user
    assert response.status_code == 200

    login_response = await open_async_client.post(
        "/api/v1/auth/login",
        json={"email": data["email"], "password": data["password"]})

    assert login_response.status_code == 200
    assert login_response.json() == {"message":"Вход успешен"}

    cookies = login_response.cookies
    auth_cookie = cookies.get("Authorization")

    assert auth_cookie is not None
    assert len(auth_cookie) > 10


@pytest.mark.asyncio
async def test_auth_logout(open_async_client, register_user, test_session):

    data, response = register_user
    assert response.status_code == 200

    login_response = await open_async_client.post(
        "/api/v1/auth/login",
        json={"email": data["email"], "password": data["password"]})

    assert login_response.status_code == 200
    assert login_response.json() == {"message": "Вход успешен"}

    auth_cookie = login_response.cookies.get("Authorization")
    assert auth_cookie is not None

    logout_response = await open_async_client.get(
        "/api/v1/auth/logout",
        headers={"Cookie": f"Authorization={auth_cookie}"}
    )
    assert logout_response.status_code == 200
    assert logout_response.json() == {"message": "Logged out"}

