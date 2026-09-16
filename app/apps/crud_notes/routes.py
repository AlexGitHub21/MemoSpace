from datetime import timedelta
from tkinter.constants import RAISED

import redis
from celery.bin.result import result
from fastapi import APIRouter, Depends, Header, HTTPException
from starlette import status
from typing import Annotated
from app.apps.auth.schemas import UserVerifySchema
from app.apps.crud_notes.schemas import NoteVerifySchema, BaseNote, UpdateNoteSchema
from app.apps.crud_notes.services import NoteService
from app.apps.auth.depends import get_current_user
from app.apps.core.core_dependency.redis_dependency import RedisDependency


crud_notes_router = APIRouter(prefix="/crud_notes", tags=["crud_notes"])


@crud_notes_router.post(
    path="/create_note",
    response_model=NoteVerifySchema,
    status_code=status.HTTP_200_OK
)
async def create_note(
        user: Annotated[UserVerifySchema, Depends(get_current_user)],
        content: BaseNote,
        idempotency_key: Annotated[str, Header(alias="Idempotency-key")],
        service: NoteService = Depends(NoteService),
        redis: RedisDependency = Depends(RedisDependency)) -> NoteVerifySchema:

    redis_key = f"idempotency:{idempotency_key}"
    async with redis.get_client() as client:

        cached_result = await client.get(redis_key)

        #если запрос такой уже выполняется
        if cached_result is not None:
            return NoteVerifySchema.model_validate_json(cached_result)

        result = await client.set(redis_key, "PENDING", ex=3600, nx=True)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Запрос уже выполняется"
            )

        note = await service.add_note(
            user_id=user.id,
            note=content
        )
        await client.set(
            redis_key,
            note.model_dump_json(),
            ex=3600
        )

        return note


@crud_notes_router.get(
    path="/get_all_notes",
    response_model=list[NoteVerifySchema] | None,
    status_code=status.HTTP_200_OK
)
async def get_all_notes(user: Annotated[UserVerifySchema, Depends(get_current_user)],
                        service: NoteService = Depends(NoteService)) -> list[NoteVerifySchema] | None:
    return await service.get_all_notes(user_id=user.id)


@crud_notes_router.delete(
    path="/delete_note",
    status_code=status.HTTP_200_OK
)
async def delete_note(user: Annotated[UserVerifySchema, Depends(get_current_user)],
                      note_id: int,
                      service: NoteService = Depends(NoteService)) -> bool:
    return await service.delete_note(user_id=user.id, note_id=note_id)


@crud_notes_router.delete(
    path="/delete_all_notes",
    status_code=status.HTTP_200_OK
)
async def delete_note(user: Annotated[UserVerifySchema, Depends(get_current_user)],
                      service: NoteService = Depends(NoteService)) -> bool:
    return await service.delete_all_notes(user_id=user.id)


@crud_notes_router.patch(
    path="/update_note",
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_note(user: Annotated[UserVerifySchema, Depends(get_current_user)],
                        data: UpdateNoteSchema,
                        service: NoteService = Depends(NoteService)) -> None:
    return await service.update_note(user_id=user.id, note_id=data.id, field=data.field, content=data.content)


@crud_notes_router.post(
    path="/note_export_pdf",
    status_code=status.HTTP_200_OK
)
async def generate_pdf(user: Annotated[UserVerifySchema, Depends(get_current_user)],
                       note_id: int,
                       idempotency_key: Annotated[str, Header(alias="Idempotency-key")],
                       service: NoteService = Depends(NoteService),
                       redis: RedisDependency = Depends(RedisDependency)) -> bool:

    redis_key = f"idempotency:{idempotency_key}"
    async with redis.get_client() as client:

        #если такого ключа нет в redis, записываем в redis ключ redis_key со значением "PENDING"
        result = await client.set(redis_key, "PENDING", ex=3600, nx=True)
        #если такой ключ есть в redis, получаем то, что хранится в redis по этому ключу
        if result is None:
            cached_result = await client.get(redis_key)

            if cached_result == "COMPLETED":
                return True

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Запрос уже выполняется"
            )

        return await service.enqueue_pdf_generation(
            user_id=user.id,
            note_id=note_id,
            idempotency_key=idempotency_key
        )