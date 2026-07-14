import json
from collections.abc import Callable
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, func, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.permissions import apply_owner_filter, assert_owner_or_admin, require_reference_write_permission
from app.db.session import get_db
from app.models import (
    Character,
    CharacterCrewSkillRelation,
    ClassName,
    CrewSkill,
    Guild,
    Item,
    Loadout,
    Operation,
    OperationBoss,
    OperationDifficulty,
    OperationLockout,
    OriginStory,
    Role,
    Spec,
    Title,
    User,
    Vehicle,
)

RelationshipConfig = tuple[str, type[Any], str]
ResourceHook = Callable[[Any, Session], None]
OWNER_SCOPED_MODELS = {Character, CharacterCrewSkillRelation, Item, Loadout, OperationLockout}
RELATIONSHIP_ID_FIELD_ALIASES = {
    "class_names": "class_name_ids",
    "characters": "character_ids",
    "difficulties": "difficulty_ids",
    "items": "item_ids",
    "loadouts": "loadout_ids",
    "related_skills": "related_skill_ids",
    "roles": "role_ids",
    "title_records": "title_ids",
    "vehicle_records": "vehicle_ids",
}


class ResourceConfig:
    def __init__(
        self,
        *,
        model: type[Any],
        path: str,
        writable_fields: set[str],
        relationship_fields: dict[str, RelationshipConfig] | None = None,
        owner_scoped: bool = False,
        admin_write: bool = False,
        before_save: ResourceHook | None = None,
    ) -> None:
        self.model = model
        self.path = path
        self.writable_fields = writable_fields
        self.relationship_fields = relationship_fields or {}
        self.owner_scoped = owner_scoped
        self.admin_write = admin_write
        self.before_save = before_save


def create_crud_router(config: ResourceConfig) -> APIRouter:
    router = APIRouter(prefix=f"/{config.path}")

    @router.get("")
    def list_records(
        page: int = Query(1, ge=1),
        per_page: int = Query(25, ge=1, le=100),
        sort: str = "id",
        order: str = Query("asc", pattern="^(asc|desc)$"),
        filter: str | None = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ) -> dict[str, Any]:
        filters = _parse_filter(filter)
        query = _apply_filters(select(config.model), config.model, filters, current_user)
        if config.owner_scoped:
            query = apply_owner_filter(query, config.model, current_user)

        total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
        query = _apply_sort(query, config.model, sort, order)
        query = query.offset((page - 1) * per_page).limit(per_page)
        records = db.scalars(query).all()
        return {"data": [_serialize(record) for record in records], "total": total}

    @router.get("/{record_id}")
    def get_record(
        record_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ) -> dict[str, Any]:
        record = _get_record_or_404(db, config.model, record_id)
        if config.owner_scoped:
            assert_owner_or_admin(record, current_user)
        return _serialize(record)

    @router.post("", status_code=status.HTTP_201_CREATED)
    def create_record(
        payload: dict[str, Any],
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ) -> dict[str, Any]:
        if config.admin_write:
            require_reference_write_permission(current_user)
        values = _extract_values(payload, config)
        try:
            record = config.model(**values)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        if config.owner_scoped:
            record.owner_id = payload.get("owner_id") if current_user.is_swtor_admin else current_user.id
            if record.owner_id is None:
                record.owner_id = current_user.id

        db.add(record)
        _assign_relationships(db, record, payload, config, current_user)
        _assert_owner_scoped_foreign_keys(db, record, current_user)
        _save_record(db, record, config)
        return _serialize(record)

    @router.patch("/{record_id}")
    def update_record(
        record_id: int,
        payload: dict[str, Any],
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ) -> dict[str, Any]:
        if config.admin_write:
            require_reference_write_permission(current_user)
        record = _get_record_or_404(db, config.model, record_id)
        if config.owner_scoped:
            assert_owner_or_admin(record, current_user)

        try:
            for field, value in _extract_values(payload, config).items():
                if field == "owner_id" and not current_user.is_swtor_admin:
                    continue
                setattr(record, field, value)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        _assign_relationships(db, record, payload, config, current_user)
        _assert_owner_scoped_foreign_keys(db, record, current_user)
        _save_record(db, record, config)
        return _serialize(record)

    @router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_record(
        record_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ) -> None:
        if config.admin_write:
            require_reference_write_permission(current_user)
        record = _get_record_or_404(db, config.model, record_id)
        if config.owner_scoped:
            assert_owner_or_admin(record, current_user)
        db.delete(record)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Record cannot be deleted.") from exc

    return router


def _parse_filter(raw_filter: str | None) -> dict[str, Any]:
    if raw_filter is None:
        return {}
    try:
        parsed = json.loads(raw_filter)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filter must be valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filter must be a JSON object.")
    return parsed


def _apply_filters(
    query: Select[Any],
    model: type[Any],
    filters: dict[str, Any],
    current_user: User,
) -> Select[Any]:
    mapper = inspect(model)
    for field, value in filters.items():
        if value is None or value == "":
            continue
        relationship_query = _apply_relationship_filter(query, model, field, value, current_user)
        if relationship_query is not None:
            query = relationship_query
            continue
        if model in {Loadout, Item}:
            relationship_query = _apply_character_link_filter(query, model, field, value)
            if relationship_query is not None:
                query = relationship_query
                continue
        if model is Character:
            relationship_query = _apply_character_relationship_filter(query, field, value)
            if relationship_query is not None:
                query = relationship_query
                continue
        if field == "q" and hasattr(model, "name"):
            query = query.where(model.name.ilike(f"%{value}%"))
            continue
        if field not in mapper.columns:
            continue
        column = getattr(model, field)
        if isinstance(value, list):
            query = query.where(column.in_(value))
        elif isinstance(value, str) and field == "name":
            query = query.where(column.ilike(f"%{value}%"))
        else:
            query = query.where(column == _coerce_column_value(column, value))
    return query


def _apply_relationship_filter(
    query: Select[Any],
    model: type[Any],
    field: str,
    value: Any,
    current_user: User,
) -> Select[Any] | None:
    if field == "mine":
        if model in OWNER_SCOPED_MODELS and bool(value):
            return query.where(model.owner_id == current_user.id)
        return query
    return None


def _apply_character_relationship_filter(
    query: Select[Any],
    field: str,
    value: Any,
) -> Select[Any] | None:
    values = value if isinstance(value, list) else [value]
    values = [filter_value for filter_value in values if filter_value not in {None, ""}]
    if not values:
        return query

    if field in {"role_id", "role_ids"}:
        return query.where(Character.roles.any(Role.id.in_(values)))
    if field in {"class_name_id", "class_name_ids"}:
        return query.where(Character.class_names.any(ClassName.id.in_(values)))
    if field in {"title_id", "title_ids"}:
        return query.where(Character.title_records.any(Title.id.in_(values)))
    if field in {"vehicle_id", "vehicle_ids"}:
        return query.where(Character.vehicle_records.any(Vehicle.id.in_(values)))
    return None


def _apply_character_link_filter(
    query: Select[Any],
    model: type[Any],
    field: str,
    value: Any,
) -> Select[Any] | None:
    values = value if isinstance(value, list) else [value]
    values = [filter_value for filter_value in values if filter_value not in {None, ""}]
    if not values:
        return query

    if field in {"character_id", "character_ids"}:
        return query.where(model.characters.any(Character.id.in_(values)))
    return None


def _apply_sort(query: Select[Any], model: type[Any], sort: str, order: str) -> Select[Any]:
    mapper = inspect(model)
    if sort not in mapper.columns:
        sort = "id"
    column = getattr(model, sort)
    return query.order_by(column.desc() if order == "desc" else column.asc())


def _extract_values(payload: dict[str, Any], config: ResourceConfig) -> dict[str, Any]:
    fields = config.writable_fields
    values = {
        field: value
        for field, value in payload.items()
        if field in fields and field not in config.relationship_fields
    }
    return _coerce_values(config.model, values)


def _coerce_values(model: type[Any], values: dict[str, Any]) -> dict[str, Any]:
    mapper = inspect(model)
    coerced: dict[str, Any] = {}
    for field, value in values.items():
        if value is None:
            coerced[field] = None
            continue
        column = mapper.columns.get(field)
        if column is not None and _column_python_type(column) is date and isinstance(value, str):
            coerced[field] = date.fromisoformat(value)
        else:
            coerced[field] = value
    return coerced


def _coerce_column_value(column: Any, value: Any) -> Any:
    if value is None:
        return None
    if _column_python_type(column) is date and isinstance(value, str):
        return date.fromisoformat(value)
    return value


def _column_python_type(column: Any) -> type[Any] | None:
    try:
        return column.type.python_type
    except NotImplementedError:
        return None


def _assign_relationships(
    db: Session,
    record: Any,
    payload: dict[str, Any],
    config: ResourceConfig,
    current_user: User,
) -> None:
    for payload_field, (relationship_name, related_model, mode) in config.relationship_fields.items():
        if payload_field not in payload:
            continue
        ids = payload[payload_field]
        if mode == "many":
            if ids is None:
                related_records = []
            elif isinstance(ids, list):
                related_records = _get_related_records(db, related_model, ids)
                _assert_related_records_allowed(related_records, current_user)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{payload_field} must be a list.")
            setattr(record, relationship_name, related_records)
        elif mode == "one":
            related_record = None if ids is None else _get_record_or_404(db, related_model, int(ids))
            if related_record is not None:
                _assert_related_records_allowed([related_record], current_user)
            setattr(record, relationship_name, related_record)


def _get_related_records(db: Session, model: type[Any], ids: list[int]) -> list[Any]:
    if not ids:
        return []
    records = db.scalars(select(model).where(model.id.in_(ids))).all()
    found_ids = {record.id for record in records}
    missing_ids = set(ids) - found_ids
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Related {model.__name__} records not found: {sorted(missing_ids)}.",
        )
    return records


def _assert_related_records_allowed(records: list[Any], current_user: User) -> None:
    if current_user.is_swtor_admin:
        return
    for record in records:
        if record.__class__ in OWNER_SCOPED_MODELS:
            assert_owner_or_admin(record, current_user)


def _assert_owner_scoped_foreign_keys(db: Session, record: Any, current_user: User) -> None:
    if current_user.is_swtor_admin:
        return

    related_records: list[Any] = []
    if isinstance(record, CharacterCrewSkillRelation) and record.character_id is not None:
        related_records.append(_get_record_or_404(db, Character, record.character_id))
    elif isinstance(record, OperationLockout) and record.character_id is not None:
        related_records.append(_get_record_or_404(db, Character, record.character_id))

    _assert_related_records_allowed(related_records, current_user)


def _save_record(db: Session, record: Any, config: ResourceConfig) -> None:
    if config.before_save is not None:
        try:
            config.before_save(record, db)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    try:
        db.commit()
    except (IntegrityError, ValueError) as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    db.refresh(record)


def _get_record_or_404(db: Session, model: type[Any], record_id: int) -> Any:
    record = db.get(model, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")
    return record


def _serialize(record: Any) -> dict[str, Any]:
    mapper = inspect(record.__class__)
    data: dict[str, Any] = {}
    for column in mapper.columns:
        value = getattr(record, column.key)
        data[column.key] = value.isoformat() if isinstance(value, date) else value
    for relationship in mapper.relationships:
        value = getattr(record, relationship.key)
        field_name = RELATIONSHIP_ID_FIELD_ALIASES.get(relationship.key, f"{relationship.key}_ids")
        if relationship.uselist:
            data[field_name] = [related.id for related in value]
        else:
            data[f"{relationship.key}_id"] = value.id if value is not None else None
    return data


def _before_save_character(record: Character, db: Session) -> None:
    if record.origin_story_id is not None:
        record.origin_story = _get_record_or_404(db, OriginStory, record.origin_story_id)
    guilds = db.scalars(select(Guild)).all()
    guild = Guild.find_or_create_from_character_guild(record, guilds)
    if guild is not None and guild not in db:
        db.add(guild)
    record.validate_character_rules()
    record.sync_derived_fields()


def _before_save_loadout(record: Loadout, db: Session) -> None:
    if record.spec_id is not None:
        record.spec = _get_record_or_404(db, Spec, record.spec_id)
    record.sync_derived_fields()


def _before_save_item(record: Item, db: Session) -> None:
    _ = db
    record.validate_item_rules()


def _before_save_crew_skill_relation(record: CharacterCrewSkillRelation, db: Session) -> None:
    if record.character_id is not None:
        record.character = _get_record_or_404(db, Character, record.character_id)
    if record.crew_skill_id is not None:
        record.crew_skill = _get_record_or_404(db, CrewSkill, record.crew_skill_id)
    record.sync_derived_fields()
    if record.character is not None:
        record.character.validate_character_rules()
        record.character.sync_derived_fields()


def _before_save_operation_lockout(record: OperationLockout, db: Session) -> None:
    if record.character_id is not None:
        record.character = _get_record_or_404(db, Character, record.character_id)
    if record.boss_id is not None:
        record.boss = _get_record_or_404(db, OperationBoss, record.boss_id)
    if record.operation_id is not None:
        record.operation = _get_record_or_404(db, Operation, record.operation_id)
    if record.difficulty_id is not None:
        record.difficulty = _get_record_or_404(db, OperationDifficulty, record.difficulty_id)
    existing = db.scalars(
        select(OperationLockout).where(
            OperationLockout.character_id == record.character_id,
            OperationLockout.boss_id == record.boss_id,
            OperationLockout.difficulty_id == record.difficulty_id,
            OperationLockout.week == record.week,
        )
    ).all()
    record.sync_derived_fields()
    record.validate_unique_lockout(existing)


def _before_save_crew_skill(record: CrewSkill, db: Session) -> None:
    _ = db
    record.validate_related_skill_rules()


def _before_save_vehicle(record: Vehicle, db: Session) -> None:
    _ = db
    record.sync_icon_metadata_from_url()


def _before_save_guild(record: Guild, db: Session) -> None:
    _ = db
    record.sync_member_count()


REFERENCE_RESOURCES = [
    ResourceConfig(
        model=CrewSkill,
        path="crew-skills",
        writable_fields={"name", "skill_type", "active", "related_skill_ids"},
        relationship_fields={"related_skill_ids": ("related_skills", CrewSkill, "many")},
        admin_write=True,
        before_save=_before_save_crew_skill,
    ),
    ResourceConfig(
        model=Operation,
        path="operations",
        writable_fields={"name", "short_name", "active", "difficulty_ids"},
        relationship_fields={"difficulty_ids": ("difficulties", OperationDifficulty, "many")},
        admin_write=True,
    ),
    ResourceConfig(
        model=OperationDifficulty,
        path="operation-difficulties",
        writable_fields={"name", "full_name", "color", "active"},
        admin_write=True,
    ),
    ResourceConfig(
        model=OperationBoss,
        path="operation-bosses",
        writable_fields={"name", "sequence", "operation_id", "active"},
        admin_write=True,
    ),
    ResourceConfig(
        model=OriginStory,
        path="origin-stories",
        writable_fields={"name", "power_type", "active"},
        admin_write=True,
    ),
    ResourceConfig(
        model=ClassName,
        path="class-names",
        writable_fields={"name", "power_type", "active", "role_ids"},
        relationship_fields={"role_ids": ("roles", Role, "many")},
        admin_write=True,
    ),
    ResourceConfig(
        model=Role,
        path="roles",
        writable_fields={"name", "color", "active", "class_name_ids"},
        relationship_fields={"class_name_ids": ("class_names", ClassName, "many")},
        admin_write=True,
    ),
    ResourceConfig(
        model=Spec,
        path="specs",
        writable_fields={"name", "role_id", "class_name_id", "mirror_spec_id", "active"},
        admin_write=True,
    ),
    ResourceConfig(
        model=Title,
        path="titles",
        writable_fields={
            "name",
            "source",
            "type",
            "operation_id",
            "operation_difficulty_id",
            "icon_filename",
            "icon_url",
            "active",
        },
        admin_write=True,
    ),
    ResourceConfig(
        model=Vehicle,
        path="vehicles",
        writable_fields={
            "name",
            "source",
            "bind",
            "operation_id",
            "operation_difficulty_id",
            "icon_filename",
            "icon_url",
            "active",
        },
        admin_write=True,
        before_save=_before_save_vehicle,
    ),
    ResourceConfig(
        model=Guild,
        path="guilds",
        writable_fields={"name", "description", "guildmaster", "member_count", "active"},
        admin_write=True,
        before_save=_before_save_guild,
    ),
]

USER_OWNED_RESOURCES = [
    ResourceConfig(
        model=Character,
        path="characters",
        writable_fields={
            "name",
            "sequence",
            "faction",
            "origin_story_id",
            "level",
            "race",
            "gender",
            "server",
            "guild",
            "alignment",
            "notes",
            "valor_rank",
            "active",
            "owner_id",
            "class_name_ids",
            "role_ids",
            "loadout_ids",
            "item_ids",
            "vehicle_ids",
            "title_ids",
        },
        relationship_fields={
            "class_name_ids": ("class_names", ClassName, "many"),
            "role_ids": ("roles", Role, "many"),
            "loadout_ids": ("loadouts", Loadout, "many"),
            "item_ids": ("items", Item, "many"),
            "vehicle_ids": ("vehicle_records", Vehicle, "many"),
            "title_ids": ("title_records", Title, "many"),
        },
        owner_scoped=True,
        before_save=_before_save_character,
    ),
    ResourceConfig(
        model=Loadout,
        path="loadouts",
        writable_fields={"name", "sequence", "loadout_type", "loadout_url", "notes", "spec_id", "active", "owner_id", "character_ids"},
        relationship_fields={"character_ids": ("characters", Character, "many")},
        owner_scoped=True,
        before_save=_before_save_loadout,
    ),
    ResourceConfig(
        model=Item,
        path="items",
        writable_fields={
            "name",
            "rarity",
            "binding",
            "bound",
            "cargo_hold",
            "cargo_bay",
            "active",
            "owner_id",
            "character_ids",
        },
        relationship_fields={"character_ids": ("characters", Character, "many")},
        owner_scoped=True,
        before_save=_before_save_item,
    ),
    ResourceConfig(
        model=CharacterCrewSkillRelation,
        path="character-crew-skill-relations",
        writable_fields={"character_id", "crew_skill_id", "level", "active", "owner_id"},
        owner_scoped=True,
        before_save=_before_save_crew_skill_relation,
    ),
    ResourceConfig(
        model=OperationLockout,
        path="operation-lockouts",
        writable_fields={"week", "character_id", "boss_id", "operation_id", "difficulty_id", "active", "owner_id"},
        owner_scoped=True,
        before_save=_before_save_operation_lockout,
    ),
]
