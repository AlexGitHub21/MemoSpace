from app.apps.admin.depends import get_current_admin
from app.apps.main import app
import pytest_asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from app.db.models.base import Base
from app.db.models import User
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.apps.core.core_dependency.dependencies import get_session
from app.apps.core.settings import db_settings
from sqlalchemy import select



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


async def override_admin():
    return User(
        id=999,
        email="admin@mail.ru",
        is_superuser=True,
    )


@pytest.mark.asyncio
async def test_get_all_users(open_async_client, register_user, test_session):
    app.dependency_overrides[get_current_admin] = override_admin
    try:
        data, response = register_user

        assert response.status_code == 200
        result = response.json()
        assert result["email"] == data["email"]

        get_users_response = await open_async_client.get(f"/api/v1/admin/users")
        assert get_users_response.status_code == 200
        assert len(get_users_response.json()) == 1
    finally:
        app.dependency_overrides.pop(get_current_admin, None)


@pytest.mark.asyncio
async def test_get_user_by_id(open_async_client, register_user, test_session):
    app.dependency_overrides[get_current_admin] = override_admin
    try:
        data, response = register_user
        assert response.status_code == 200

        result = response.json()

        get_response1 = await open_async_client.get(f"/api/v1/admin/users/{result['id']}")
        result_get_response1 = get_response1.json()
        assert get_response1.status_code == 200
        assert result_get_response1["email"] == data["email"]


        get_response2 = await open_async_client.get("/api/v1/admin/users/2")
        assert get_response2.status_code == 404
        assert get_response2.json() == {"detail": "User not found"}
    finally:
        app.dependency_overrides.pop(get_current_admin, None)


#!!!!
@pytest.mark.asyncio
async def test_update_status_user(open_async_client, register_user, test_session):
    app.dependency_overrides[get_current_admin] = override_admin
    try:
        data, response = register_user
        assert response.status_code == 200

        result = await test_session.execute(
            select(User).where(User.email == data["email"])
        )
        test_user = result.scalar_one_or_none()

        assert test_user is not None
        assert test_user.is_superuser is False

        response = await open_async_client.patch(
            f"/api/v1/admin/users/{test_user.id}",
            json={"is_superuser": True})

        assert response.status_code == 200
        await test_session.refresh(test_user)
        result = await test_session.execute(
            select(User).where(User.email == data["email"])
        )
        test_user = result.scalar_one_or_none()

        assert test_user.is_superuser is True
        # assert response.json()["is_superuser"] is True
    finally:
        app.dependency_overrides.pop(get_current_admin, None)


@pytest.mark.asyncio
async def test_delete_user(open_async_client, register_user, test_session):
    app.dependency_overrides[get_current_admin] = override_admin
    try:
        data, response = register_user
        assert response.status_code == 200

        result = await test_session.execute(
            select(User).where(User.email == data["email"])
        )
        test_user = result.scalar_one_or_none()
        assert test_user is not None

        delete_response = await open_async_client.delete(
            f"/api/v1/admin/users/{test_user.id}"
        )
        assert delete_response.status_code == 204
    finally:
        app.dependency_overrides.pop(get_current_admin, None)