import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from starlette.authentication import requires
from raystack.contrib.auth.users.models import UserModel
import bcrypt


# JWT settings
try:
    from config.settings import SECRET_KEY, ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
except ImportError:
    SECRET_KEY = "your-secret-key-here"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except jwt.PyJWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    email = verify_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await UserModel.objects.filter(email=email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


# Password handling functions (stubs)
async def hash_password(password: str) -> str:
    # Hash password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


async def check_password(plain_password: str, hashed_password: str) -> bool:
    # Verify password using bcrypt
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def generate_jwt(user_id: int) -> str:
    # JWT token generation
    data = {"sub": str(user_id)}
    return create_access_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


# Additional functions for various authentication methods
async def get_current_user_from_token(token: str):
    return await get_current_user(token)


async def get_current_active_user_from_token(token: str):
    return await get_current_active_user(await get_current_user(token))


async def get_current_active_superuser_from_token(token: str):
    return await get_current_active_superuser(await get_current_user(token))


async def get_current_user_from_cookie(request):
    # Get user from cookie
    token = request.cookies.get("jwt")
    if token:
        return await get_current_user(token)
    return None


async def get_current_active_user_from_cookie(request):
    user = await get_current_user_from_cookie(request)
    if user:
        return await get_current_active_user(user)
    return None


async def get_current_active_superuser_from_cookie(request):
    user = await get_current_user_from_cookie(request)
    if user:
        return await get_current_active_superuser(user)
    return None


async def get_current_user_from_header(request):
    # Get user from header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        return await get_current_user(token)
    return None


async def get_current_active_user_from_header(request):
    user = await get_current_user_from_header(request)
    if user:
        return await get_current_active_user(user)
    return None


async def get_current_active_superuser_from_header(request):
    user = await get_current_user_from_header(request)
    if user:
        return await get_current_active_superuser(user)
    return None


async def get_current_user_from_query(request):
    # Get user from query parameter
    token = request.query_params.get("token")
    if token:
        return await get_current_user(token)
    return None


async def get_current_active_user_from_query(request):
    user = await get_current_user_from_query(request)
    if user:
        return await get_current_active_user(user)
    return None


async def get_current_active_superuser_from_query(request):
    user = await get_current_user_from_query(request)
    if user:
        return await get_current_active_superuser(user)
    return None


async def get_current_user_from_body(request):
    # Get user from body
    body = await request.json()
    token = body.get("token")
    if token:
        return await get_current_user(token)
    return None


async def get_current_active_user_from_body(request):
    user = await get_current_user_from_body(request)
    if user:
        return await get_current_active_user(user)
    return None


async def get_current_active_superuser_from_body(request):
    user = await get_current_user_from_body(request)
    if user:
        return await get_current_active_superuser(user)
    return None

