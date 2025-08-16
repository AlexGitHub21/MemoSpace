from apps.core.settings import settings
from redis.asyncio import ConnectionPool, Redis
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
class RedisDependency():

    def __init__(self):
        self._url = settings.redis_settings.redis_url
        self._pool: ConnectionPool = self._init_pool()

    def _init_pool(self) -> ConnectionPool:
        return ConnectionPool.from_url(url=self._url, encoding="utf8", decode_responses=True)

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator:
        redis_client = Redis(connection_pool=self._pool)
        try:
            yield redis_client
        finally:
            await redis_client.aclose()