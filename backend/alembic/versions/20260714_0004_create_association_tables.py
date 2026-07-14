"""create association tables

Revision ID: 20260714_0004
Revises: 20260714_0003
Create Date: 2026-07-14
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260714_0004"
down_revision: str | None = "20260714_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def create_association_table(table_name: str, left_column: str, left_target: str, right_column: str, right_target: str) -> None:
    op.create_table(
        table_name,
        sa.Column(left_column, sa.Integer(), nullable=False),
        sa.Column(right_column, sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint([left_column], [left_target]),
        sa.ForeignKeyConstraint([right_column], [right_target]),
        sa.PrimaryKeyConstraint(left_column, right_column),
    )
    op.create_index(f"ix_{table_name}_{left_column}", table_name, [left_column], unique=False)
    op.create_index(f"ix_{table_name}_{right_column}", table_name, [right_column], unique=False)


def drop_association_table(table_name: str, left_column: str, right_column: str) -> None:
    op.drop_index(f"ix_{table_name}_{right_column}", table_name=table_name)
    op.drop_index(f"ix_{table_name}_{left_column}", table_name=table_name)
    op.drop_table(table_name)


def upgrade() -> None:
    create_association_table("character_class_names", "character_id", "characters.id", "class_name_id", "class_names.id")
    create_association_table("character_roles", "character_id", "characters.id", "role_id", "roles.id")
    create_association_table("character_loadouts", "character_id", "characters.id", "loadout_id", "loadouts.id")
    create_association_table("character_items", "character_id", "characters.id", "item_id", "items.id")
    create_association_table("character_vehicles", "character_id", "characters.id", "vehicle_id", "vehicles.id")
    create_association_table("character_titles", "character_id", "characters.id", "title_id", "titles.id")
    create_association_table("class_name_roles", "class_name_id", "class_names.id", "role_id", "roles.id")
    create_association_table(
        "crew_skill_related_skills",
        "skill_id",
        "crew_skills.id",
        "related_skill_id",
        "crew_skills.id",
    )
    create_association_table(
        "operation_difficulties_rel",
        "operation_id",
        "operations.id",
        "difficulty_id",
        "operation_difficulties.id",
    )


def downgrade() -> None:
    drop_association_table("operation_difficulties_rel", "operation_id", "difficulty_id")
    drop_association_table("crew_skill_related_skills", "skill_id", "related_skill_id")
    drop_association_table("class_name_roles", "class_name_id", "role_id")
    drop_association_table("character_titles", "character_id", "title_id")
    drop_association_table("character_vehicles", "character_id", "vehicle_id")
    drop_association_table("character_items", "character_id", "item_id")
    drop_association_table("character_loadouts", "character_id", "loadout_id")
    drop_association_table("character_roles", "character_id", "role_id")
    drop_association_table("character_class_names", "character_id", "class_name_id")
