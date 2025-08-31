from fastapi import APIRouter, FastAPI

from .urls import router as urls_router

from raystack.middlewares import PermissionMiddleware


router = APIRouter()
# router.include_router(urls_router, prefix="/admin", include_in_schema=False)
router.include_router(urls_router, prefix="/admin", tags=["restricted"])
