from apps.auth.schemas import GetUserByID, UserVerifySchema
from apps.crud_notes.schemas import BaseNote, NoteVerifySchema
from apps.crud_notes.managers import NoteManager
from fastapi import Depends


class NoteService:
    def __init__(self, manager: NoteManager = Depends(NoteManager)) -> None:
        self.manager = manager

    async def add_note(self, user_id: int, note: BaseNote) -> NoteVerifySchema:
        return await self.manager.create_note(user_id=user_id, note=note)

    async def get_all_notes(self, user_id: int) -> list[NoteVerifySchema]:
        return await self.manager.get_all_notes_by_user(user_id=user_id)

    async def delete_note(self, user_id: int, note_id) -> bool:
        return await self.manager.delete_note_by_user(user_id=user_id, note_id=note_id)

    async def delete_all_notes(self, user_id: int) -> bool:
        return await self.manager.delete_all_notes_by_user(user_id=user_id)

    async def update_note(self, user_id: int, note_id: int, field: str, content: str) -> bool:
        return await self.manager.update_note_by_user(user_id=user_id, note_id=note_id, field=field, content=content)

