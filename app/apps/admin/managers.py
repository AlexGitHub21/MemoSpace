import uuid
from fastapi import Depends, HTTPException
from app.apps.admin.schemas import UpdateUserStatusSchema
from app.db.models import User
from sqlalchemy import update, select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.apps.core.core_dependency.dependencies import get_session
from app.apps.admin.schemas import UserReturnData, AdminVerifySchema

class AdminManager:
    def __init__(self, db_session: AsyncSession = Depends(get_session)) -> None:
        self.db_session = db_session
        self.model = User

    async def delete_user_by_id(self, user_id: int) -> bool:
        query = (
            delete(self.model).where(self.model.id == user_id)
        )

        try:
            result = await self.db_session.execute(query)
            await self.db_session.commit()

            return result.rowcount > 0

        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def get_users(self) -> list[UserReturnData]:
        query = (
            select(self.model)
        )

        result = await self.db_session.execute(query)
        users = result.scalars().all()

        return [UserReturnData.model_validate(user) for user in users]


    async def get_user_by_id(self, user_id: int) -> UserReturnData:
        query = (
            select(self.model).where(self.model.id == user_id)
        )

        result = await self.db_session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return UserReturnData.model_validate(user)

    async def update_status_user(self, user_id: int, data: UpdateUserStatusSchema) -> UserReturnData:
        query = (
            update(self.model)
        .where(
            self.model.id == user_id
        ).values(is_superuser = data.is_superuser))

        try:
            await self.db_session.execute(query)
            await self.db_session.commit()

            return await self.get_user_by_id(user_id)
        except SQLAlchemyError:
            await self.db_session.rollback()
            raise

    async def get_admin_by_id(self, user_id: uuid.UUID | str) -> AdminVerifySchema | None:
        query = select(
            self.model.id,
            self.model.email,
            self.model.is_superuser,
        ).where(self.model.id == user_id)

        result = await self.db_session.execute(query)
        user = result.mappings().one_or_none()

        if user:
            return AdminVerifySchema(**user)
        return None