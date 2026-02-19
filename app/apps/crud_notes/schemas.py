from pydantic import BaseModel, ConfigDict
from typing import Union


class BaseNote(BaseModel):
    title: str
    content: str
    tags: Union[str | list[int]] | None = None
    is_public: bool = False


class NoteVerifySchema(BaseNote):
    id: int
    author_id: int

    model_config = ConfigDict(from_attributes=True)


class UpdateNoteSchema(BaseModel):
    id: int
    field: str
    content: str