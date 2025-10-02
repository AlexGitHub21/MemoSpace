from fastapi import APIRouter
from apps.auth.routes import auth_router
from apps.crud_notes.routes import crud_notes_router

apps_router = APIRouter(prefix="/api/v1")

apps_router.include_router(router=auth_router)
apps_router.include_router(router=crud_notes_router)
