from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class IdMixin:
    id: Mapped[int] = mapped_column(primary_key=True, index=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ActiveMixin:
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")


class OwnedModelMixin:
    @declared_attr
    def owner_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey("users.id"), nullable=False, index=True)
