from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: int
    name: str
    pass


class Post(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str]
    is_public: bool
    publish_at: datetime | None = None
    pass


class Comment(BaseModel):
    author_id: int
    content: str
    publish_at: datetime | None = None
    pass
