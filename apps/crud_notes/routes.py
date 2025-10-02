from fastapi import APIRouter, Depends
from starlette import status
from typing import Annotated
from apps.auth.schemas import UserVerifySchema
from apps.crud_notes.schemas import NoteVerifySchema, BaseNote
from apps.crud_notes.services import NoteService
from apps.auth.depends import get_current_user

crud_notes_router = APIRouter(prefix="/crud_notes", tags=["crud_notes"])


@crud_notes_router.post(
    path="/create_note",
    response_model=NoteVerifySchema,
    status_code=status.HTTP_200_OK
)
async def create_note(user: Annotated[UserVerifySchema, Depends(get_current_user)],
                      content: BaseNote, service: NoteService = Depends(NoteService)) -> NoteVerifySchema:
    return await service.add_note(user_id=user.id, note=content)