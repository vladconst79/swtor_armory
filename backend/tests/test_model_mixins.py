from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.models.mixins import ActiveMixin, IdMixin, OwnedModelMixin, TimestampMixin
from app.models.user import User


class ModelTestBase(DeclarativeBase):
    pass


class OwnedModel(IdMixin, TimestampMixin, ActiveMixin, OwnedModelMixin, ModelTestBase):
    __tablename__ = "owned_models"

    name: Mapped[str] = mapped_column(nullable=False)


def test_user_uses_shared_id_and_timestamp_fields() -> None:
    columns = inspect(User).columns

    assert columns.id.primary_key is True
    assert columns.id.index is True
    assert columns.created_at.nullable is False
    assert columns.updated_at.nullable is False
    assert columns.updated_at.onupdate is not None


def test_owned_model_mixin_adds_shared_record_fields() -> None:
    columns = inspect(OwnedModel).columns

    assert columns.id.primary_key is True
    assert columns.created_at.nullable is False
    assert columns.updated_at.nullable is False
    assert columns.active.nullable is False
    assert columns.owner_id.nullable is False
    assert columns.owner_id.index is True
    assert any(foreign_key.target_fullname == "users.id" for foreign_key in columns.owner_id.foreign_keys)
