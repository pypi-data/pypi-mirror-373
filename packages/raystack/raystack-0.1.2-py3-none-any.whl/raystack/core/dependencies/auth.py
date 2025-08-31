from collections.abc import Generator
from typing import Union

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session
from starlette.authentication import SimpleUser # Import SimpleUser from Starlette

# Lazy import to avoid errors when loading
# from raystack.core.database.base import get_async_db, get_sync_engine
from raystack.core.security.jwt import create_access_token, TokenPayload # Import TokenPayload
from raystack.contrib.auth.users.models import UserModel # Import UserModel

# Lazy imports to avoid circular dependencies

def get_api_v1_str():
    try:
        from raystack.conf import get_settings
        return getattr(get_settings(), 'API_V1_STR', '/api/v1')
    except ImportError:
        return '/api/v1'

def get_secret_key():
    try:
        from raystack.conf import get_settings
        return getattr(get_settings(), 'SECRET_KEY', 'default-secret-key')
    except ImportError:
        return 'default-secret-key'

def get_algorithm():
    try:
        from raystack.conf import get_settings
        return getattr(get_settings(), 'ALGORITHM', 'HS256')
    except ImportError:
        return 'HS256'

_reusable_oauth2 = None

def get_reusable_oauth2():
    global _reusable_oauth2
    if _reusable_oauth2 is None:
        _reusable_oauth2 = OAuth2PasswordBearer(
            tokenUrl=f"{get_api_v1_str()}/login/access-token"
        )
    return _reusable_oauth2

def get_db():
    try:
        from raystack.core.database.base import get_sync_engine
        with Session(get_sync_engine()) as session: # Use get_sync_engine() to create synchronous session
            yield session
    except ImportError:
        # Fallback if database is not configured
        raise RuntimeError("Database is not configured")

# For Python 3.6 compatibility, we'll use regular types instead of Annotated
SessionDep = Session
TokenDep = str
UserDep = Union[UserModel, SimpleUser] # Define UserDep to handle both UserModel and SimpleUser

def get_current_user(request: Request, session: SessionDep, token: TokenDep = Depends(get_reusable_oauth2)) -> UserModel:
    # First, check if user is already authenticated by middleware
    if "user" in request.scope and request.scope["user"] is not None:
        simple_user: SimpleUser = request.scope["user"]
        # Assuming SimpleUser.identity is the user ID
        user_id = int(simple_user.identity)
        user = session.get(UserModel, user_id)
        if user:
            if not user.is_active:
                raise HTTPException(status_code=400, detail="Inactive user")
            return user
        
    # If not authenticated by middleware, try to authenticate via JWT token from header
    try:
        payload = jwt.decode(
            token, get_secret_key(), algorithms=[get_algorithm()]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(UserModel, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

CurrentUser = UserModel

def get_current_active_superuser(current_user: CurrentUser) -> UserModel:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user