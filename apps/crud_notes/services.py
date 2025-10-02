from apps.auth.schemas import GetUserByID, UserVerifySchema
from apps.crud_notes.schemas import BaseNote, NoteVerifySchema
from apps.crud_notes.managers import NoteManager
from fastapi import Depends



class NoteService:
    def __init__(self, manager: NoteManager = Depends(NoteManager)) -> None:
        self.manager = manager

    async def add_note(self, user_id: int, note: BaseNote) -> NoteVerifySchema:
        return await self.manager.create_note(user_id=user_id, note=note)
