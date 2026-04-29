from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.apps.core.settings import *


engine = create_async_engine(
            url=db_settings.get_db_url,
            echo=db_settings.DB_ECHO,
            pool_pre_ping=True
        )

SessionLocal = async_sessionmaker(
            bind=engine, expire_on_commit=False, autocommit=False
        )
