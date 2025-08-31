import os
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from raystack.shortcuts import render_template
from raystack.contrib.auth.groups.forms import GroupCreateForm, GroupUpdateForm
from raystack.contrib.auth.groups.models import GroupModel
from raystack.contrib.auth.users.models import UserModel
import jwt
from jwt import PyJWTError as JWTError
from datetime import timedelta, datetime
# from .utils import hash_password, generate_jwt, check_password

from starlette.responses import JSONResponse, \
    PlainTextResponse, \
    RedirectResponse, \
    StreamingResponse, \
    FileResponse, \
    HTMLResponse

from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse

router = APIRouter()

        # Create table when starting application
@router.on_event("startup")
async def create_tables():
    GroupModel.create_table()
    owners_group = await GroupModel.objects.filter(name="Owners").first()  # type: ignore
    if not owners_group:
        GroupModel.objects.create(name="Owners")

        # (Commented examples of models and endpoints left for history)
