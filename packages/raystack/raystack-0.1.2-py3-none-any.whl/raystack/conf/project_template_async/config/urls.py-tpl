from fastapi import APIRouter, Request


router = APIRouter()

# Import your routers and include your urls here
from apps.{{ app_name }}.urls import router as home_urls

# Example:
# from apps.example.urls import router as example_urls
router.include_router(home_urls, include_in_schema=False)
