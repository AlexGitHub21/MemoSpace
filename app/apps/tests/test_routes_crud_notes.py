from app.apps.auth.depends import get_current_user
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
from app.apps.auth.schemas import UserVerifySchema


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


@pytest_asyncio.fixture
async def authenticated_user(open_async_client, register_user):
    data, response = register_user
    assert response.status_code == 200

    user_id = response.json().get("id")

    async def override_user():
        return User(
            id=user_id,
            email=data["email"],
            is_superuser=False,
        )

    app.dependency_overrides[get_current_user] = override_user

    yield user_id

    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_note(open_async_client, authenticated_user):

    response_create_note = await open_async_client.post(
        "/api/v1/crud_notes/create_note",
        json={"title": "title1", "content": "desc1"}
    )

    assert response_create_note.status_code == 200


@pytest.mark.asyncio
async def test_get_all_notes(open_async_client, authenticated_user):

    response_create_note1 = await open_async_client.post(
        "/api/v1/crud_notes/create_note",
        json={"title": "title1", "content": "desc1"}
    )
    assert response_create_note1.status_code == 200

    response_create_note2 = await open_async_client.post(
        "/api/v1/crud_notes/create_note",
        json={"title": "title222", "content": "desc222"}
    )
    assert response_create_note2.status_code == 200

    response_get_all_notes = await open_async_client.get(
        "/api/v1/crud_notes/get_all_notes")

    assert response_get_all_notes.status_code == 200
    assert len(response_get_all_notes.json()) == 2
    assert response_get_all_notes.json()[0]["title"] == "title1"
    assert response_get_all_notes.json()[1]["title"] == "title222"


@pytest.mark.asyncio
async def test_delete_note(open_async_client, authenticated_user):

    response_create_note1 = await open_async_client.post(
        "/api/v1/crud_notes/create_note",
        json={"title": "title1", "content": "desc1"}
    )
    assert response_create_note1.status_code == 200

    response_create_note2 = await open_async_client.post(
        "/api/v1/crud_notes/create_note",
        json={"title": "title222", "content": "desc222"}
    )
    assert response_create_note2.status_code == 200

    response_get_all_notes = await open_async_client.get(
        "/api/v1/crud_notes/get_all_notes")

    assert response_get_all_notes.status_code == 200
    assert len(response_get_all_notes.json()) == 2
    assert response_get_all_notes.json()[0]["title"] == "title1"
    assert response_get_all_notes.json()[1]["title"] == "title222"

    response_delete_note = await open_async_client.delete(
        f"/api/v1/crud_notes/delete_note?note_id={response_create_note2.json().get('id')}"
    )
    assert response_delete_note.status_code == 200
    response_get_all_notes = await open_async_client.get(
        "/api/v1/crud_notes/get_all_notes")

    assert response_get_all_notes.status_code == 200
    assert len(response_get_all_notes.json()) == 1



@pytest.mark.asyncio
async def test_delete_all_notes(open_async_client, authenticated_user):

    response_create_note1 = await open_async_client.post(
        "/api/v1/crud_notes/create_note",
        json={"title": "title1", "content": "desc1"}
    )
    assert response_create_note1.status_code == 200

    response_create_note2 = await open_async_client.post(
        "/api/v1/crud_notes/create_note",
        json={"title": "title222", "content": "desc222"}
    )
    assert response_create_note2.status_code == 200

    response_get_all_notes = await open_async_client.get(
        "/api/v1/crud_notes/get_all_notes"
    )

    assert response_get_all_notes.status_code == 200
    assert len(response_get_all_notes.json()) == 2
    assert response_get_all_notes.json()[0]["title"] == "title1"
    assert response_get_all_notes.json()[1]["title"] == "title222"

    response_delete_note = await open_async_client.delete(
        "/api/v1/crud_notes/delete_all_notes"
    )
    assert response_delete_note.status_code == 200
    assert response_delete_note.json() == True

    response_get_all_notes = await open_async_client.get(
        "/api/v1/crud_notes/get_all_notes"
    )
    assert response_get_all_notes.status_code == 200




@pytest.mark.asyncio
async def test_update_note(open_async_client, authenticated_user):

    response_create_note1 = await open_async_client.post(
        "/api/v1/crud_notes/create_note",
        json={"title": "title1", "content": "desc1"}
    )
    assert response_create_note1.status_code == 200

    response_update_note = await open_async_client.patch(
        f"/api/v1/crud_notes/update_note",
        json={"id": response_create_note1.json().get('id'),
              "field": "title",
              "content": "description"
              }
    )
    assert response_update_note.status_code == 204






