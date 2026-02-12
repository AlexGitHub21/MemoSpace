from apps.main import app
import pytest_asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from db.models.base import Base
from db.models import User
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from apps.core.core_dependency.db_dependency import DBDependency
from apps.core.settings import db_settings
from apps.auth.handlers import AuthHandler


TEST_DATABASE_URL = f"mysql+aiomysql://{db_settings.DB_USER}:{db_settings.DB_SETTINGS.get_secret_value()}" \
                    f"@{db_settings.DB_HOST}:{db_settings.DB_PORT}/{db_settings.DB_NAME}"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False, autocommit=False)


@pytest_asyncio.fixture
async def test_session() -> AsyncSession:
    async with TestSessionLocal() as session:
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


@pytest_asyncio.fixture(autouse=True)
def mock_send_email():
    with patch("apps.auth.tasks.send_confirmation_email.delay") as mock_task:
        yield mock_task


@pytest_asyncio.fixture(autouse=True)
async def mock_redis():
    mock_redis = AsyncMock()
    mock_redis.__aenter__.return_value = mock_redis
    mock_redis.__aexit__.return_value = None
    with patch("apps.core.core_dependency.redis_dependency.RedisDependency.get_client",
               return_value=mock_redis
    ):
        yield mock_redis



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
async def test_auth_register(open_async_client, register_user, mock_send_email):
    data, response = register_user

    assert response.status_code == 200
    result = response.json()
    assert result["email"] == data["email"]
    mock_send_email.assert_called_once()


@pytest.mark.asyncio
async def test_auth_confirm_register(open_async_client, register_user, mock_send_email):
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
async def test_auth_login(open_async_client, mock_redis, test_session):
    email = "example@mail.ru"
    password = "passwordLosh24598"
    hash_password = await AuthHandler().get_password_hash(password)

    test_user = User(email=email, hashed_password=hash_password)
    test_session.add(test_user)
    await test_session.commit()
    await test_session.refresh(test_user)

    response = await open_async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password})

    assert response.status_code == 200
    assert response.json() == {"message":"Вход успешен"}

    cookies = response.cookies
    auth_cookie = cookies.get("Authorization")

    assert auth_cookie is not None
    assert len(auth_cookie) > 10


@pytest.mark.asyncio
async def test_auth_logout(open_async_client, test_session):
    email = "example@mail.ru"
    password = "passwordLosh24598"
    hash_password = await AuthHandler().get_password_hash(password)

    test_user = User(email=email, hashed_password=hash_password)
    test_session.add(test_user)
    await test_session.commit()
    await test_session.refresh(test_user)

    response = await open_async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password})

    assert response.status_code == 200
    assert response.json() == {"message": "Вход успешен"}

    auth_cookie = response.cookies.get("Authorization")
    assert auth_cookie is not None

    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as open_async_client:
        response = await open_async_client.get(
            "/api/v1/auth/logout",
            headers={"Cookie": f"Authorization={auth_cookie}"}
        )
    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}


@pytest.mark.asyncio
async def test_create_note(test_session):
    pass

