import os

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse

# from raystack.conf import settings
from raystack.shortcuts import render_template
from raystack.contrib.auth.users.forms import UserCreateForm, UserUpdateForm
from raystack.contrib.auth.users.models import UserModel
from raystack.contrib.auth.groups.models import GroupModel
from raystack.contrib.auth.accounts.forms import LoginForm
from raystack.contrib.auth.accounts.utils import hash_password, generate_jwt, check_password
from raystack.contrib.auth.accounts.utils import get_current_user, get_current_active_user
from raystack.contrib.auth.accounts.utils import get_current_active_superuser
from raystack.contrib.auth.accounts.utils import get_current_user_from_token
from raystack.contrib.auth.accounts.utils import get_current_active_user_from_token
from raystack.contrib.auth.accounts.utils import get_current_active_superuser_from_token
from raystack.contrib.auth.accounts.utils import get_current_user_from_cookie
from raystack.contrib.auth.accounts.utils import get_current_active_user_from_cookie
from raystack.contrib.auth.accounts.utils import get_current_active_superuser_from_cookie
from raystack.contrib.auth.accounts.utils import get_current_user_from_header
from raystack.contrib.auth.accounts.utils import get_current_active_user_from_header
from raystack.contrib.auth.accounts.utils import get_current_active_superuser_from_header
from raystack.contrib.auth.accounts.utils import get_current_user_from_query
from raystack.contrib.auth.accounts.utils import get_current_active_user_from_query
from raystack.contrib.auth.accounts.utils import get_current_active_superuser_from_query
from raystack.contrib.auth.accounts.utils import get_current_user_from_body
from raystack.contrib.auth.accounts.utils import get_current_active_user_from_body
from raystack.contrib.auth.accounts.utils import get_current_active_superuser_from_body
import jwt
from jwt import PyJWTError as JWTError

from fastapi.security import OAuth2PasswordBearer


router = APIRouter()


def url_for(endpoint, **kwargs):
    """
    Function for generating URL based on endpoint and additional parameters.
    In this case, the endpoint is ignored as we only use the filename.
    """
    if not kwargs:
        return f"/{endpoint}"
    
    path = f"/{endpoint}"
    for key, value in kwargs.items():
        path += f"/{value}"
    
    return path


@router.get("/login", response_model=None)
async def test(request: Request):    
    return render_template(request=request, template_name="accounts/login.html", context={
        "url_for": url_for,
        "parent": "home",
        "segment": "test",
        "config": request.app.settings,
    })

@router.post("/login", response_model=None)
async def login_post(request: Request):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")

    user = await UserModel.objects.filter(email=email).first()

    if user and await check_password(password, user.password_hash):
        # Generate JWT token
        token = generate_jwt(user.id)
        
        response = RedirectResponse(url="/admin/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="jwt", value=token, httponly=True) # Secure cookie
        return response
    else:
        return RedirectResponse(url="/accounts/login?error=invalid_credentials", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/register", response_model=None)
async def test(request: Request):
    return render_template(request=request, template_name="accounts/register.html", context={
        "url_for": url_for,
        "parent": "home",
        "segment": "test",
        "config": request.app.settings,
    })

@router.get("/password_change", response_model=None)
async def test(request: Request):    
    return render_template(request=request, template_name="accounts/password_change.html", context={
        "url_for": url_for,
        "parent": "/",
        "segment": "test",
        "config": request.app.settings,
    })