from apps.core.core_dependency.db_dependency import DBDependency
from fastapi import Depends
from db.models import Post
from apps.core.core_dependency.redis_dependency import RedisDependency
from apps.crud_notes.schemas import BaseNote, NoteVerifySchema
from sqlalchemy.exc import IntegrityError


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

            return NoteVerifySchema.from_orm(new_note)


    async def get_all_notes_by_user(self) -> dict:
        pass


    async def delete_note_by_user(self):
        pass


    async def delete_all_notes_by_user(self):
        pass


    async def update_note_by_user(self):
        pass