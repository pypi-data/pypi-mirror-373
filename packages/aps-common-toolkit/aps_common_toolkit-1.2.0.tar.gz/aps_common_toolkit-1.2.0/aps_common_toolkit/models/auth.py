from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel


class SuperUserMixin:
    """
    Mixin for superuser attributes.
    """

    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_staff: Mapped[bool] = mapped_column(default=False, nullable=False)


class User(BaseModel):
    """
    Model for creating users table.
    """

    __abstract__ = True

    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)
    last_login: Mapped[datetime] = mapped_column(nullable=True)

    def __str__(self):
        return self.email
