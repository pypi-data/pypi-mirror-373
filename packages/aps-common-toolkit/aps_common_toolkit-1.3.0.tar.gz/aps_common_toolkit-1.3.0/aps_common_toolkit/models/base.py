from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


def now():
    return datetime.now(timezone.utc)


class BaseModel(DeclarativeBase):
    """
    Base class for all models.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=now)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, default=None, onupdate=now
    )
