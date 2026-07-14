"""add character rule fields

Revision ID: 20260714_0006
Revises: 20260714_0005
Create Date: 2026-07-14
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260714_0006"
down_revision: str | None = "20260714_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("characters", sa.Column("faction_icon", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column("characters", "faction_icon")
