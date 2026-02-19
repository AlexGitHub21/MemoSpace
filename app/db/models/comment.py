from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mixins.id_mixins import IDMixin
from app.db.mixins.timestamp_mixins import TimestampsMixin
from app.db.mixins.content_mixins import ContentMixin
from app.db.models.base import Base
from app.db.models.user import User


class Comment(IDMixin, ContentMixin, TimestampsMixin, Base):
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    author: Mapped["User"] = relationship(back_populates="comments")
