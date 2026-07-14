"""create reference tables

Revision ID: 20260714_0003
Revises: 20260714_0002
Create Date: 2026-07-14
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260714_0003"
down_revision: str | None = "20260714_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def shared_reference_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("active", sa.Boolean(), server_default="true", nullable=False),
    ]


def create_shared_indexes(table_name: str) -> None:
    op.create_index(f"ix_{table_name}_id", table_name, ["id"], unique=False)


def drop_shared_indexes(table_name: str) -> None:
    op.drop_index(f"ix_{table_name}_id", table_name=table_name)


def upgrade() -> None:
    op.create_table(
        "crew_skills",
        *shared_reference_columns(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("skill_type", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("crew_skills")
    op.create_index("ix_crew_skills_name", "crew_skills", ["name"], unique=True)
    op.create_index("ix_crew_skills_skill_type", "crew_skills", ["skill_type"], unique=False)

    op.create_table(
        "operations",
        *shared_reference_columns(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("short_name", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("operations")
    op.create_index("ix_operations_name", "operations", ["name"], unique=True)
    op.create_index("ix_operations_short_name", "operations", ["short_name"], unique=False)

    op.create_table(
        "operation_difficulties",
        *shared_reference_columns(),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("color", sa.Integer(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("operation_difficulties")
    op.create_index("ix_operation_difficulties_name", "operation_difficulties", ["name"], unique=True)

    op.create_table(
        "origin_stories",
        *shared_reference_columns(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("power_type", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("origin_stories")
    op.create_index("ix_origin_stories_name", "origin_stories", ["name"], unique=True)
    op.create_index("ix_origin_stories_power_type", "origin_stories", ["power_type"], unique=False)

    op.create_table(
        "class_names",
        *shared_reference_columns(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("power_type", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("class_names")
    op.create_index("ix_class_names_name", "class_names", ["name"], unique=True)
    op.create_index("ix_class_names_power_type", "class_names", ["power_type"], unique=False)

    op.create_table(
        "roles",
        *shared_reference_columns(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("color", sa.Integer(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("roles")
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    op.create_table(
        "guilds",
        *shared_reference_columns(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("guildmaster", sa.String(length=255), nullable=True),
        sa.Column("member_count", sa.Integer(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("guilds")
    op.create_index("ix_guilds_name", "guilds", ["name"], unique=True)

    op.create_table(
        "operation_bosses",
        *shared_reference_columns(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sequence", sa.Integer(), server_default="10", nullable=False),
        sa.Column("operation_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["operation_id"], ["operations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("operation_bosses")
    op.create_index("ix_operation_bosses_name", "operation_bosses", ["name"], unique=False)
    op.create_index("ix_operation_bosses_operation_id", "operation_bosses", ["operation_id"], unique=False)

    op.create_table(
        "specs",
        *shared_reference_columns(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("class_name_id", sa.Integer(), nullable=False),
        sa.Column("mirror_spec_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["class_name_id"], ["class_names.id"]),
        sa.ForeignKeyConstraint(["mirror_spec_id"], ["specs.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("specs")
    op.create_index("ix_specs_name", "specs", ["name"], unique=False)
    op.create_index("ix_specs_role_id", "specs", ["role_id"], unique=False)
    op.create_index("ix_specs_class_name_id", "specs", ["class_name_id"], unique=False)
    op.create_index("ix_specs_mirror_spec_id", "specs", ["mirror_spec_id"], unique=False)

    op.create_table(
        "titles",
        *shared_reference_columns(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("operation_id", sa.Integer(), nullable=True),
        sa.Column("operation_difficulty_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["operation_difficulty_id"], ["operation_difficulties.id"]),
        sa.ForeignKeyConstraint(["operation_id"], ["operations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("titles")
    op.create_index("ix_titles_name", "titles", ["name"], unique=False)
    op.create_index("ix_titles_source", "titles", ["source"], unique=False)
    op.create_index("ix_titles_type", "titles", ["type"], unique=False)
    op.create_index("ix_titles_operation_id", "titles", ["operation_id"], unique=False)
    op.create_index("ix_titles_operation_difficulty_id", "titles", ["operation_difficulty_id"], unique=False)

    op.create_table(
        "vehicles",
        *shared_reference_columns(),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("bind", sa.String(length=50), nullable=True),
        sa.Column("operation_id", sa.Integer(), nullable=True),
        sa.Column("operation_difficulty_id", sa.Integer(), nullable=True),
        sa.Column("icon_filename", sa.String(length=255), nullable=True),
        sa.Column("icon_url", sa.String(length=2048), nullable=True),
        sa.ForeignKeyConstraint(["operation_difficulty_id"], ["operation_difficulties.id"]),
        sa.ForeignKeyConstraint(["operation_id"], ["operations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    create_shared_indexes("vehicles")
    op.create_index("ix_vehicles_name", "vehicles", ["name"], unique=False)
    op.create_index("ix_vehicles_source", "vehicles", ["source"], unique=False)
    op.create_index("ix_vehicles_bind", "vehicles", ["bind"], unique=False)
    op.create_index("ix_vehicles_operation_id", "vehicles", ["operation_id"], unique=False)
    op.create_index("ix_vehicles_operation_difficulty_id", "vehicles", ["operation_difficulty_id"], unique=False)

    with op.batch_alter_table("characters") as batch_op:
        batch_op.create_foreign_key("fk_characters_origin_story_id_origin_stories", "origin_stories", ["origin_story_id"], ["id"])
        batch_op.create_foreign_key("fk_characters_guild_id_guilds", "guilds", ["guild_id"], ["id"])

    with op.batch_alter_table("loadouts") as batch_op:
        batch_op.create_foreign_key("fk_loadouts_role_id_roles", "roles", ["role_id"], ["id"])
        batch_op.create_foreign_key("fk_loadouts_spec_id_specs", "specs", ["spec_id"], ["id"])

    with op.batch_alter_table("character_crew_skill_relations") as batch_op:
        batch_op.create_foreign_key(
            "fk_character_crew_skill_relations_crew_skill_id_crew_skills",
            "crew_skills",
            ["crew_skill_id"],
            ["id"],
        )

    with op.batch_alter_table("operation_lockouts") as batch_op:
        batch_op.create_foreign_key("fk_operation_lockouts_boss_id_operation_bosses", "operation_bosses", ["boss_id"], ["id"])
        batch_op.create_foreign_key("fk_operation_lockouts_operation_id_operations", "operations", ["operation_id"], ["id"])
        batch_op.create_foreign_key(
            "fk_operation_lockouts_difficulty_id_operation_difficulties",
            "operation_difficulties",
            ["difficulty_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("operation_lockouts") as batch_op:
        batch_op.drop_constraint("fk_operation_lockouts_difficulty_id_operation_difficulties", type_="foreignkey")
        batch_op.drop_constraint("fk_operation_lockouts_operation_id_operations", type_="foreignkey")
        batch_op.drop_constraint("fk_operation_lockouts_boss_id_operation_bosses", type_="foreignkey")

    with op.batch_alter_table("character_crew_skill_relations") as batch_op:
        batch_op.drop_constraint("fk_character_crew_skill_relations_crew_skill_id_crew_skills", type_="foreignkey")

    with op.batch_alter_table("loadouts") as batch_op:
        batch_op.drop_constraint("fk_loadouts_spec_id_specs", type_="foreignkey")
        batch_op.drop_constraint("fk_loadouts_role_id_roles", type_="foreignkey")

    with op.batch_alter_table("characters") as batch_op:
        batch_op.drop_constraint("fk_characters_guild_id_guilds", type_="foreignkey")
        batch_op.drop_constraint("fk_characters_origin_story_id_origin_stories", type_="foreignkey")

    op.drop_index("ix_vehicles_operation_difficulty_id", table_name="vehicles")
    op.drop_index("ix_vehicles_operation_id", table_name="vehicles")
    op.drop_index("ix_vehicles_bind", table_name="vehicles")
    op.drop_index("ix_vehicles_source", table_name="vehicles")
    op.drop_index("ix_vehicles_name", table_name="vehicles")
    drop_shared_indexes("vehicles")
    op.drop_table("vehicles")

    op.drop_index("ix_titles_operation_difficulty_id", table_name="titles")
    op.drop_index("ix_titles_operation_id", table_name="titles")
    op.drop_index("ix_titles_type", table_name="titles")
    op.drop_index("ix_titles_source", table_name="titles")
    op.drop_index("ix_titles_name", table_name="titles")
    drop_shared_indexes("titles")
    op.drop_table("titles")

    op.drop_index("ix_specs_mirror_spec_id", table_name="specs")
    op.drop_index("ix_specs_class_name_id", table_name="specs")
    op.drop_index("ix_specs_role_id", table_name="specs")
    op.drop_index("ix_specs_name", table_name="specs")
    drop_shared_indexes("specs")
    op.drop_table("specs")

    op.drop_index("ix_operation_bosses_operation_id", table_name="operation_bosses")
    op.drop_index("ix_operation_bosses_name", table_name="operation_bosses")
    drop_shared_indexes("operation_bosses")
    op.drop_table("operation_bosses")

    op.drop_index("ix_guilds_name", table_name="guilds")
    drop_shared_indexes("guilds")
    op.drop_table("guilds")

    op.drop_index("ix_roles_name", table_name="roles")
    drop_shared_indexes("roles")
    op.drop_table("roles")

    op.drop_index("ix_class_names_power_type", table_name="class_names")
    op.drop_index("ix_class_names_name", table_name="class_names")
    drop_shared_indexes("class_names")
    op.drop_table("class_names")

    op.drop_index("ix_origin_stories_power_type", table_name="origin_stories")
    op.drop_index("ix_origin_stories_name", table_name="origin_stories")
    drop_shared_indexes("origin_stories")
    op.drop_table("origin_stories")

    op.drop_index("ix_operation_difficulties_name", table_name="operation_difficulties")
    drop_shared_indexes("operation_difficulties")
    op.drop_table("operation_difficulties")

    op.drop_index("ix_operations_short_name", table_name="operations")
    op.drop_index("ix_operations_name", table_name="operations")
    drop_shared_indexes("operations")
    op.drop_table("operations")

    op.drop_index("ix_crew_skills_skill_type", table_name="crew_skills")
    op.drop_index("ix_crew_skills_name", table_name="crew_skills")
    drop_shared_indexes("crew_skills")
    op.drop_table("crew_skills")
