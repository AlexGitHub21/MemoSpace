from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Text, String


class ContentMixin:
    content: Mapped[str] = mapped_column(String(500), unique=False, nullable=False)
