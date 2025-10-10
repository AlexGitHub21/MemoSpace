from fastapi import APIRouter, Depends
from starlette import status
from typing import Annotated
from apps.auth.schemas import UserVerifySchema
from apps.crud_notes.schemas import NoteVerifySchema, BaseNote, UpdateNoteSchema
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


@crud_notes_router.get(
    path="/get_all_notes",
    response_model=list[NoteVerifySchema],
    status_code=status.HTTP_200_OK
)
async def get_all_notes(user: Annotated[UserVerifySchema, Depends(get_current_user)],
                        service: NoteService = Depends(NoteService)) -> list[NoteVerifySchema]:
    return await service.get_all_notes(user_id=user.id)


@crud_notes_router.post(
    path="/delete_note",
    status_code=status.HTTP_200_OK
)
async def delete_note(user: Annotated[UserVerifySchema, Depends(get_current_user)],
                      note_id: int,
                      service: NoteService = Depends(NoteService)) -> bool:
    return await service.delete_note(user_id=user.id, note_id=note_id)


@crud_notes_router.post(
    path="/delete_all_notes",
    status_code=status.HTTP_200_OK
)
async def delete_note(user: Annotated[UserVerifySchema, Depends(get_current_user)],
                      service: NoteService = Depends(NoteService)) -> bool:
    return await service.delete_all_notes(user_id=user.id)


@crud_notes_router.post(
    path="/update_note",
    status_code=status.HTTP_200_OK
)
async def update_note(user: Annotated[UserVerifySchema, Depends(get_current_user)],
                        data: UpdateNoteSchema,
                      service: NoteService = Depends(NoteService)) -> bool:
    return await service.update_note(user_id=user.id, note_id=data.id, field=data.field, content=data.content)