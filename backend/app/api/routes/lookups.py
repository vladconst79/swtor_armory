from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.db.session import get_db
from app.models import (
    ClassName,
    CrewSkill,
    Guild,
    Operation,
    OperationBoss,
    OperationDifficulty,
    OriginStory,
    Role,
    Spec,
    Title,
    User,
    Vehicle,
)

router = APIRouter(prefix="/lookups")

LOOKUP_MODELS: dict[str, type[Any]] = {
    "crew-skills": CrewSkill,
    "operations": Operation,
    "operation-bosses": OperationBoss,
    "operation-difficulties": OperationDifficulty,
    "origin-stories": OriginStory,
    "class-names": ClassName,
    "roles": Role,
    "specs": Spec,
    "titles": Title,
    "vehicles": Vehicle,
    "guilds": Guild,
}


@router.get("/{resource_name}")
def lookup_records(
    resource_name: str,
    q: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, list[dict[str, Any]]]:
    _ = current_user
    model = LOOKUP_MODELS.get(resource_name)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lookup resource not found.")
    query = select(model)
    if q and hasattr(model, "name"):
        query = query.where(model.name.ilike(f"%{q}%"))
    if hasattr(model, "name"):
        query = query.order_by(model.name.asc())
    else:
        query = query.order_by(model.id.asc())
    records = db.scalars(query.limit(limit)).all()
    return {
        "data": [
            {
                "id": record.id,
                "name": getattr(record, "name", str(record.id)),
            }
            for record in records
        ]
    }
