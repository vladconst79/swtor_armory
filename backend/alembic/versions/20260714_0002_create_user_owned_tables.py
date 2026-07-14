"""create user owned tables

Revision ID: 20260714_0002
Revises: 20260714_0001
Create Date: 2026-07-14
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260714_0002"
down_revision: str | None = "20260714_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def add_shared_owned_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
    ]


def create_shared_indexes(table_name: str) -> None:
    op.create_index(f"ix_{table_name}_id", table_name, ["id"], unique=False)
    op.create_index(f"ix_{table_name}_owner_id", table_name, ["owner_id"], unique=False)


def drop_shared_indexes(table_name: str) -> None:
    op.drop_index(f"ix_{table_name}_owner_id", table_name=table_name)
    op.drop_index(f"ix_{table_name}_id", table_name=table_name)


def upgrade() -> None:
    op.create_table(
        "characters",
        *add_shared_owned_columns(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("sequence", sa.Integer(), server_default="10", nullable=False),
        sa.Column("faction", sa.String(length=50), nullable=False),
        sa.Column("origin_story_id", sa.Integer(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.Column("race", sa.String(length=50), nullable=True),
        sa.Column("gender", sa.String(length=50), nullable=True),
        sa.Column("server", sa.String(length=50), nullable=True),
        sa.Column("guild", sa.String(length=255), nullable=True),
        sa.Column("guild_id", sa.Integer(), nullable=True),
        sa.Column("alignment", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("valor_rank", sa.Integer(), nullable=True),
        sa.Column("crew_skills_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("mounts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("titles", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("characters")
    op.create_index("ix_characters_name", "characters", ["name"], unique=False)
    op.create_index("ix_characters_origin_story_id", "characters", ["origin_story_id"], unique=False)
    op.create_index("ix_characters_server", "characters", ["server"], unique=False)
    op.create_index("ix_characters_guild_id", "characters", ["guild_id"], unique=False)

    op.create_table(
        "loadouts",
        *add_shared_owned_columns(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sequence", sa.Integer(), server_default="10", nullable=False),
        sa.Column("loadout_type", sa.String(length=50), nullable=False),
        sa.Column("loadout_url", sa.String(length=2048), nullable=True),
        sa.Column("loadout_iframe", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.Column("spec_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("loadouts")
    op.create_index("ix_loadouts_role_id", "loadouts", ["role_id"], unique=False)
    op.create_index("ix_loadouts_spec_id", "loadouts", ["spec_id"], unique=False)

    op.create_table(
        "items",
        *add_shared_owned_columns(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("rarity", sa.String(length=50), server_default="common", nullable=False),
        sa.Column("binding", sa.String(length=50), server_default="none", nullable=False),
        sa.Column("bound", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("cargo_hold", sa.String(length=50), server_default="cargo_hold", nullable=False),
        sa.Column("cargo_bay", sa.Integer(), server_default="1", nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("items")
    op.create_index("ix_items_name", "items", ["name"], unique=False)
    op.create_index("ix_items_rarity", "items", ["rarity"], unique=False)
    op.create_index("ix_items_binding", "items", ["binding"], unique=False)
    op.create_index("ix_items_bound", "items", ["bound"], unique=False)
    op.create_index("ix_items_cargo_hold", "items", ["cargo_hold"], unique=False)
    op.create_index("ix_items_cargo_bay", "items", ["cargo_bay"], unique=False)

    op.create_table(
        "character_crew_skill_relations",
        *add_shared_owned_columns(),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("character_id", sa.Integer(), nullable=False),
        sa.Column("crew_skill_id", sa.Integer(), nullable=False),
        sa.Column("level", sa.Integer(), server_default="1", nullable=False),
        sa.Column("skill_type", sa.String(length=50), nullable=True),
        sa.Column("progress", sa.Float(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("character_crew_skill_relations")
    op.create_index(
        "ix_character_crew_skill_relations_character_id",
        "character_crew_skill_relations",
        ["character_id"],
        unique=False,
    )
    op.create_index(
        "ix_character_crew_skill_relations_crew_skill_id",
        "character_crew_skill_relations",
        ["crew_skill_id"],
        unique=False,
    )

    op.create_table(
        "operation_lockouts",
        *add_shared_owned_columns(),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("week", sa.Date(), nullable=True),
        sa.Column("character_id", sa.Integer(), nullable=False),
        sa.Column("boss_id", sa.Integer(), nullable=False),
        sa.Column("operation_id", sa.Integer(), nullable=False),
        sa.Column("difficulty_id", sa.Integer(), nullable=False),
        sa.Column("completion_rate", sa.Float(), server_default="0", nullable=False),
        sa.Column("faction", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("operation_lockouts")
    op.create_index("ix_operation_lockouts_week", "operation_lockouts", ["week"], unique=False)
    op.create_index("ix_operation_lockouts_character_id", "operation_lockouts", ["character_id"], unique=False)
    op.create_index("ix_operation_lockouts_boss_id", "operation_lockouts", ["boss_id"], unique=False)
    op.create_index("ix_operation_lockouts_operation_id", "operation_lockouts", ["operation_id"], unique=False)
    op.create_index("ix_operation_lockouts_difficulty_id", "operation_lockouts", ["difficulty_id"], unique=False)
    op.create_index("ix_operation_lockouts_faction", "operation_lockouts", ["faction"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_operation_lockouts_faction", table_name="operation_lockouts")
    op.drop_index("ix_operation_lockouts_difficulty_id", table_name="operation_lockouts")
    op.drop_index("ix_operation_lockouts_operation_id", table_name="operation_lockouts")
    op.drop_index("ix_operation_lockouts_boss_id", table_name="operation_lockouts")
    op.drop_index("ix_operation_lockouts_character_id", table_name="operation_lockouts")
    op.drop_index("ix_operation_lockouts_week", table_name="operation_lockouts")
    drop_shared_indexes("operation_lockouts")
    op.drop_table("operation_lockouts")

    op.drop_index("ix_character_crew_skill_relations_crew_skill_id", table_name="character_crew_skill_relations")
    op.drop_index("ix_character_crew_skill_relations_character_id", table_name="character_crew_skill_relations")
    drop_shared_indexes("character_crew_skill_relations")
    op.drop_table("character_crew_skill_relations")

    op.drop_index("ix_items_cargo_bay", table_name="items")
    op.drop_index("ix_items_cargo_hold", table_name="items")
    op.drop_index("ix_items_bound", table_name="items")
    op.drop_index("ix_items_binding", table_name="items")
    op.drop_index("ix_items_rarity", table_name="items")
    op.drop_index("ix_items_name", table_name="items")
    drop_shared_indexes("items")
    op.drop_table("items")

    op.drop_index("ix_loadouts_spec_id", table_name="loadouts")
    op.drop_index("ix_loadouts_role_id", table_name="loadouts")
    drop_shared_indexes("loadouts")
    op.drop_table("loadouts")

    op.drop_index("ix_characters_guild_id", table_name="characters")
    op.drop_index("ix_characters_server", table_name="characters")
    op.drop_index("ix_characters_origin_story_id", table_name="characters")
    op.drop_index("ix_characters_name", table_name="characters")
    drop_shared_indexes("characters")
    op.drop_table("characters")
