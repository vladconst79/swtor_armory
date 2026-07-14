"""add binary columns

Revision ID: 20260714_0005
Revises: 20260714_0004
Create Date: 2026-07-14
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260714_0005"
down_revision: str | None = "20260714_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("class_names", sa.Column("class_icon", sa.LargeBinary(), nullable=True))
    op.add_column("roles", sa.Column("icon", sa.LargeBinary(), nullable=True))
    op.add_column("titles", sa.Column("icon", sa.LargeBinary(), nullable=True))
    op.add_column("titles", sa.Column("icon_filename", sa.String(length=255), nullable=True))
    op.add_column("titles", sa.Column("icon_url", sa.String(length=2048), nullable=True))
    op.add_column("vehicles", sa.Column("icon", sa.LargeBinary(), nullable=True))
    op.add_column("guilds", sa.Column("image", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column("guilds", "image")
    op.drop_column("vehicles", "icon")
    op.drop_column("titles", "icon_url")
    op.drop_column("titles", "icon_filename")
    op.drop_column("titles", "icon")
    op.drop_column("roles", "icon")
    op.drop_column("class_names", "class_icon")
