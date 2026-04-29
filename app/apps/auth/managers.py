import uuid
from app.apps.core.core_dependency.dependencies import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from app.db.models import User
from app.apps.auth.schemas import CreateUser, UserReturnData, GetUserWithIDAndEmail, UserVerifySchema
from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError
from app.apps.core.core_dependency.redis_dependency import RedisDependency


class UserManager:
    def __init__(self, db_session: AsyncSession = Depends(get_session), redis: RedisDependency = Depends(RedisDependency)) -> None:
        self.db_session = db_session
        self.model = User
        self.redis = redis

    async def create_user(self, user: CreateUser) -> UserReturnData:
        new_user = self.model(**user.model_dump())

        self.db_session.add(new_user)
        try:
            await self.db_session.commit()
            await self.db_session.refresh(new_user)
        except IntegrityError:
            await self.db_session.rollback()
            raise HTTPException(status_code=400, detail="User already Exists.")

        return UserReturnData(**new_user.__dict__)

    async def confirm_user(self, email: str) -> None:
        query = (
            update(self.model)
            .where(self.model.email == email)
            .values(is_verified=True, is_active=True)
        )
        try:
            await self.db_session.execute(query)
            await self.db_session.commit()
        except IntegrityError:
            await self.db_session.rollback()
            raise

    async def get_user_by_email(self, email: str) -> GetUserWithIDAndEmail | None:
        query = select(
                self.model.id,
                self.model.email,
                self.model.hashed_password
        ).where(self.model.email == email)

        result = await self.db_session.execute(query)
        user = result.mappings().first()

        if user:
            return GetUserWithIDAndEmail(**user)
        return None

    async def store_access_token(self, token: str, user_id: uuid.UUID | str, session_id: str) -> None:
        async with self.redis.get_client() as client:
            await client.set(f"{user_id}:{session_id}", token)

    async def get_access_token(self, user_id: uuid.UUID | str, session_id: str) -> str | None:
        async with self.redis.get_client() as client:
            return await client.get(f"{user_id}:{session_id}")

    async def get_user_by_id(self, user_id: uuid.UUID | str) -> UserVerifySchema | None:
        query = select(
            self.model.id,
            self.model.email
        ).where(self.model.id == user_id)

        result = await self.db_session.execute(query)
        user = result.mappings().one_or_none()

        if user:
            return UserVerifySchema(**user)
        return None

    async def revoke_access_token(self, user_id: uuid.UUID | str, session_id: str) -> None:
        async with self.redis.get_client() as client:
            await client.delete(f"{user_id}:{session_id}")



