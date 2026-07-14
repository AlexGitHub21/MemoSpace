from app.apps.core.core_dependency.dependencies import get_session
from fastapi import Depends
from app.db.models import Post
from app.apps.core.core_dependency.redis_dependency import RedisDependency
from app.apps.crud_notes.schemas import BaseNote, NoteVerifySchema
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, delete
from typing import Optional
from app.apps.logs.logging_config import memospace_logger


class NoteManager:
    def __init__(self, db_session: AsyncSession = Depends(get_session), redis: RedisDependency = Depends(RedisDependency)) -> None:
        self.db_session = db_session
        self.model = Post
        self.redis = redis

    async def create_note(self, user_id: int, note: BaseNote) -> NoteVerifySchema:
        new_note = self.model(**note.model_dump(),
                              author_id=user_id,
                              )
        self.db_session.add(new_note)
        try:
            await self.db_session.commit()
            await self.db_session.refresh(new_note)
            memospace_logger.info(f"Пользователь {user_id} создал заметку {new_note.id}")
        except IntegrityError:
            await self.db_session.rollback()
            memospace_logger.error(f"Заметка не создана для пользователя {user_id}")
            raise

        return NoteVerifySchema.model_validate(new_note)

    async def get_all_notes_by_user(self, user_id: int) -> list[NoteVerifySchema] | None:
        query = select(self.model).where(self.model.author_id == user_id)

        result = await self.db_session.execute(query)
        notes = result.scalars().all()
        if notes:
            return [NoteVerifySchema.model_validate(note) for note in notes]
        else:
            memospace_logger.warning(f"Заметки для пользователя {user_id} не найдены в базе данных")
            return None

    async def delete_note_by_user(self, user_id: int, note_id: int) -> bool:
        query = (
            delete(self.model).where(
                self.model.id == note_id,
                self.model.author_id == user_id)
        )

        try:
            result = await self.db_session.execute(query)
            await self.db_session.commit()
            memospace_logger.warning(f"Заметка с id {note_id} успешно удалена для пользователя {user_id}")
            return result.rowcount > 0

        except SQLAlchemyError:
            await self.db_session.rollback()
            memospace_logger.warning(f"Заметка с id {note_id} не удалена для пользователя {user_id}")
            raise

    async def delete_all_notes_by_user(self, user_id: int) -> bool:
        query = (
            delete(self.model).where(
                self.model.author_id == user_id)
        )

        try:
            result = await self.db_session.execute(query)
            await self.db_session.commit()
            memospace_logger.warning(f"Все заметки успешно удалены для пользователя {user_id}")
            return result.rowcount > 0

        except SQLAlchemyError:
            await self.db_session.rollback()
            memospace_logger.warning(f"Заметки для пользователя {user_id} не найдены/удалены")
            raise

    async def update_note_by_user(self, user_id: int, note_id: int, field: str, content: str) -> None:
        allowed_fields = {"title", "content", "tags", "is_public"}
        if field not in allowed_fields:
            raise ValueError(f"Поле '{field}' нельзя обновлять")

        query = (
            update(self.model)
            .where(
                self.model.id == note_id,
                self.model.author_id == user_id)
            .values({ field: content })
        )
        try:
            await self.db_session.execute(query)
            await self.db_session.commit()
            memospace_logger.info(f"Успешно обновилась заметка {note_id} пользователя {user_id}")
        except SQLAlchemyError:
            await self.db_session.rollback()
            memospace_logger.error(f"Не удалось обновить содержимое заметки {note_id} для пользователя {user_id}")
            raise

    async def get_note(self, user_id: int, note_id: int) -> Optional[dict]:
        query = select(
            self.model.tags,
            self.model.title,
            self.model.content,
            self.model.created_at,
            self.model.updated_at
        ).where(self.model.id == note_id,
                self.model.author_id == user_id)

        result = await self.db_session.execute(query)
        note = result.mappings().one_or_none()
        return dict(note) if note else None
