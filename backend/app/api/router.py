from fastapi import APIRouter

from app.api.routes import crud
from app.api.routes import auth
from app.api.routes import health
from app.api.routes import lookups
from app.api.routes import users

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(lookups.router, tags=["lookups"])
api_router.include_router(users.router, tags=["users"])

for resource in [*crud.REFERENCE_RESOURCES, *crud.USER_OWNED_RESOURCES]:
    api_router.include_router(crud.create_crud_router(resource), tags=[resource.path])
