from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from .base import BaseModel, now


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


class OutstandingToken(BaseModel):
    """
    Model for storing outstanding JWT tokens.
    """

    __abstract__ = True
    __tablename__ = "outstanding_tokens"

    id = None  # type: ignore[assignment]
    jti: Mapped[str] = mapped_column(
        nullable=False, unique=True, index=True, primary_key=True
    )
    token: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)

    @declared_attr
    def blacklist_entry(cls) -> Mapped["BlacklistedToken"]:
        return relationship(
            "BlacklistedToken",
            back_populates="outstanding_entry",
            uselist=False,
            passive_deletes=True,
        )

    def __str__(self) -> str:
        return self.jti


class BlacklistedToken(BaseModel):
    """
    Model for storing blacklisted JWT tokens.
    """

    __abstract__ = True
    __tablename__ = "blacklisted_tokens"

    token_jti: Mapped[str] = mapped_column(
        ForeignKey("outstanding_tokens.jti", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    blacklisted_at: Mapped[datetime] = mapped_column(nullable=False, default=now)

    @declared_attr
    def outstanding_entry(cls) -> Mapped["OutstandingToken"]:
        return relationship(
            "OutstandingToken",
            back_populates="blacklist_entry",
        )

    def __str__(self) -> str:
        return self.token_jti
