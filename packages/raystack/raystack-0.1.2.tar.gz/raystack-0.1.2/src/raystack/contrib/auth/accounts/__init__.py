from fastapi import APIRouter

from .urls import router as urls_router
from .api import router as api_router

router = APIRouter()
# router.include_router(urls_router, prefix="/admin", include_in_schema=False)
router.include_router(urls_router, prefix="/accounts", tags=["render"])
router.include_router(api_router, prefix="/accounts", tags=["api"])