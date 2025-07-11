from sqlalchemy import Boolean, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.mixins.id_mixins import IDMixin
from db.mixins.timestamp_mixins import TimestampsMixin
from db.mixins.content_mixins import ContentMixin
from db.models.base import Base
from db.models.user import User


class Post(IDMixin, ContentMixin, TimestampsMixin, Base):
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    tags: Mapped[str] = mapped_column(String(100), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    author: Mapped["User"] = relationship(back_populates="posts")
