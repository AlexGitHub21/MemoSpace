from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.mixins.id_mixins import IDMixin
from db.mixins.timestamp_mixins import TimestampsMixin
from db.mixins.content_mixins import ContentMixin
from db.models.base import Base
from db.models.user import User


class Comment(IDMixin, ContentMixin, TimestampsMixin, Base):
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    author: Mapped["User"] = relationship(back_populates="comments")
