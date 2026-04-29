from typing import AsyncGenerator
from app.apps.core.core_dependency.db_session import SessionLocal


async def get_session() -> AsyncGenerator:
    async with SessionLocal() as session:
        yield session