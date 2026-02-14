from apps.core.core_dependency.db_dependency import DBDependency
from fastapi import Depends
from db.models import Post
from apps.core.core_dependency.redis_dependency import RedisDependency
from apps.crud_notes.schemas import BaseNote, NoteVerifySchema
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import update, select, delete
from typing import Optional


class NoteManager:
    def __init__(self, db: DBDependency = Depends(DBDependency), redis: RedisDependency = Depends(RedisDependency)) -> None:
        self.db = db
        self.model = Post
        self.redis = redis

    async def create_note(self, user_id: int, note: BaseNote) -> NoteVerifySchema:
        async with self.db.db_session() as session:
            new_note = self.model(**note.model_dump(),
                                  author_id=user_id,
                                  )
            session.add(new_note)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()

            return NoteVerifySchema.model_validate(new_note)

    async def get_all_notes_by_user(self, user_id: int) -> list[NoteVerifySchema] | None:
        async with self.db.db_session() as session:
            query = select(self.model).where(self.model.author_id == user_id)

            result = await session.execute(query)
            notes = result.scalars().all()
            if notes:
                return [NoteVerifySchema.model_validate(note) for note in notes]
            else:
                return None

    async def delete_note_by_user(self, user_id: int, note_id: int) -> bool:
        async with self.db.db_session() as session:
            query = (
                delete(self.model).where(
                    self.model.id == note_id,
                    self.model.author_id == user_id)
            )

            try:
                result = await session.execute(query)
                await session.commit()
                return True
            except SQLAlchemyError:
                await session.rollback()
                return False

    async def delete_all_notes_by_user(self, user_id: int) -> bool:
        async with self.db.db_session() as session:
            query = (
                delete(self.model).where(
                    self.model.author_id == user_id)
            )

            try:
                await session.execute(query)
                await session.commit()
                return True
            except SQLAlchemyError:
                await session.rollback()
                return False

    async def update_note_by_user(self, user_id: int, note_id: int, field: str, content: str) -> bool:
        allowed_fields = {"title", "content", "tags", "is_public"}
        if field not in allowed_fields:
            raise ValueError(f"Поле '{field}' нельзя обновлять")

        async with self.db.db_session() as session:
            query = (
                update(self.model)
                .where(
                    self.model.id == note_id,
                    self.model.author_id == user_id)
                .values({ field: content })
            )
            try:
                await session.execute(query)
                await session.commit()
                return True
            except SQLAlchemyError:
                await session.rollback()
                return False

    async def get_note(self, user_id: int, note_id: int) -> Optional[dict]:
        async with self.db.db_session() as session:
            query = select(
                self.model.tags,
                self.model.title,
                self.model.content,
                self.model.created_at,
                self.model.updated_at
            ).where(self.model.id == note_id,
                    self.model.author_id == user_id)

            result = await session.execute(query)
            note = result.mappings().one_or_none()
            return dict(note) if note else None
