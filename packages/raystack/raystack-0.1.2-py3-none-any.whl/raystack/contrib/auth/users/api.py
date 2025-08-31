from typing import Union, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import jwt
from jwt import PyJWTError as JWTError
from datetime import timedelta
from .models import UserModel, UserCreate, User
from .utils import hash_password, generate_jwt, check_password

from starlette.responses import JSONResponse, \
    PlainTextResponse, \
    RedirectResponse, \
    StreamingResponse, \
    FileResponse, \
    HTMLResponse

from raystack.core.database.sqlalchemy import db
from raystack.contrib.auth.groups.models import GroupModel

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

# Pydantic model for user login
class UserLogin(BaseModel):
    email: str
    password: str

# Pydantic model for token
class Token(BaseModel):
    access_token: str
    token_type: str

# Pydantic model for token data
class TokenData(BaseModel):
    email: Union[str] = None


# JWT settings
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.route("/login", methods=["POST"])
async def login_user(request):
    # Redirect to previous path after login
    if 'history' in request.session and len(request.session['history']):
        previous = request.session['history'].pop()
    else:
        previous = '/admin'

    # Get form data
    form = await request.form()
    username = form["email"]
    password = form["password"]

    # Search for user in database
    user = await UserModel.objects.filter(email=username).first()  # type: ignore
    if not user:
        return RedirectResponse(previous, status_code=303)

    hashed_pass = user.password_hash

    # Check password
    valid_pass = await check_password(password, hashed_pass)
    if not valid_pass:
        return RedirectResponse(previous, status_code=303)

    if previous in ('/users/login', '/users/login/', "/"):
        previous = '/admin'

    response = RedirectResponse(previous, status_code=303)
    if valid_pass:
        response.set_cookie('jwt', generate_jwt(user.id), httponly=True)
    return response


@router.post("/logout", response_model=None)
def logout():
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie("jwt")
    return response


# Create new user (POST)
@router.post("/", response_model=None)
async def create_user(user: UserCreate):
    hashed_password = await hash_password(user.password)
    group = await GroupModel.objects.filter(id=user.group_id).first()  # type: ignore
    
    # Check if user doesn't exist
    existing_user = await UserModel.objects.filter(email=user.email).first()  # type: ignore
    if existing_user:
        return JSONResponse(
            status_code=400,
            content={"message": "User with this email already exists"}
        )

    new_user = await UserModel.objects.create(
        name=user.name,
        age=user.age,
        email=user.email,
        password_hash=hashed_password,
        group=group.id
    )
    return User(
        id=new_user.id,
        name=new_user.name,
        age=new_user.age,
        email=new_user.email,
        group=new_user.group.id
    )


# Get all users (GET)
@router.get("/", response_model=List[User])
async def get_users():
    users = await UserModel.objects.all().execute()  # type: ignore
    return [User(name=user.name, age=user.age, email=user.email) for user in users] 