"""
Raystack built-in authentication (users, groups, accounts).
"""

from fastapi import APIRouter

from raystack.contrib.auth.users import api as users_api
from raystack.contrib.auth.groups import api as groups_api
from raystack.contrib.auth.accounts import urls as accounts_urls
from raystack.contrib.auth.accounts import api as accounts_api

# Import models for convenience
from raystack.contrib.auth.users.models import UserModel, User, UserCreate
from raystack.contrib.auth.groups.models import GroupModel, Group

__all__ = [
    'UserModel', 'User', 'UserCreate',
    'GroupModel', 'Group',
    'router'
]

router = APIRouter()

# Connect user routes
if hasattr(users_api, 'router'):
    router.include_router(users_api.router, prefix="/users", tags=["users"])
# Connect group routes
if hasattr(groups_api, 'router'):
    router.include_router(groups_api.router, prefix="/groups", tags=["groups"])
# Connect account routes (registration, authentication, password change)
if hasattr(accounts_urls, 'router'):
    router.include_router(accounts_urls.router, prefix="/accounts", tags=["accounts"])
# Connect account routes (login/logout)
if hasattr(accounts_api, 'router'):
    router.include_router(accounts_api.router, prefix="/accounts", tags=["accounts"])
