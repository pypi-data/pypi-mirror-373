from fastapi import APIRouter

from .api import router as api_router
from .urls import router as urls_router

router = APIRouter()
router.include_router(urls_router, include_in_schema=False)
router.include_router(api_router, prefix="/api", tags=[])