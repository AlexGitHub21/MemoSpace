from db.db_dependency import DBDependency
from fastapi import Depends, HTTPException
from db.models import User
from apps.auth.schemas import CreateUser, UserReturnData
from sqlalchemy import insert, update
from sqlalchemy.exc import IntegrityError


class UserManager:
    def __init__(self, db: DBDependency = Depends(DBDependency)):
        self.db = db
        self.model = User

    async def create_user(self, user: CreateUser) -> UserReturnData:
        async with self.db.db_session() as session:
            new_user = self.model(**user.model_dump())

            session.add(new_user)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=400, detail="User already Exists.")

            await session.refresh(new_user)
            return UserReturnData(**new_user.__dict__)

    async def confirm_user(self, email: str) -> None:
        async with self.db.db_session() as session:
            query = (
                update(self.model)
                .where(self.model.email == email)
                .values(is_verified=True, is_active=True)
            )
            await session.execute(query)
            await session.commit()

