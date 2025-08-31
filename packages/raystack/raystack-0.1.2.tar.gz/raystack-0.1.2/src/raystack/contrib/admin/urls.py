import os

from fastapi import APIRouter, Request

from raystack.conf import settings
from raystack.shortcuts import render_template

from fastapi import Depends, HTTPException, status
import jwt
from jwt import PyJWTError as JWTError

from fastapi.security import OAuth2PasswordBearer

from raystack.contrib.auth.accounts.decorators import login_required

from raystack.contrib.auth.users.models import UserModel
from raystack.contrib.auth.groups.models import GroupModel
from raystack.contrib.auth.groups.forms import GroupCreateForm


router = APIRouter()


def url_for(endpoint, **kwargs):
    """
    Function for generating URL based on endpoint and additional parameters.
    In this case, endpoint is ignored as we only use filename.
    """
    path = f"/{endpoint}"

    if not kwargs:
        return path
    
    for key, value in kwargs.items():
        path += f"/{value}"
    
    return path


@router.get("/users", response_model=None)
@login_required(["user_auth"])
async def users_view(request: Request):
    users = await UserModel.objects.all().execute_all()  # type: ignore
    # for user in users:
    #     print("user", user)

    return render_template(request=request, template_name="admin/users.html", context={
        "url_for": url_for,
        "parent": "/",
        "segment": "test",
        "config": request.app.settings,
        "users": users,
    })


@router.get("/groups", response_model=None)
@login_required(["user_auth"])
async def groups_view(request: Request):
    groups = await GroupModel.objects.all().execute()  # type: ignore

    return render_template(request=request, template_name="admin/groups.html", context={
        "url_for": url_for,
        "parent": "/",
        "segment": "test",
        "config": request.app.settings,
        "groups": groups,
    })


@router.get("/", response_model=None)
@login_required(["user_auth"])
async def index_view(request: Request):    
    return render_template(request=request, template_name="pages/index.html", context={
        "url_for": url_for,
        "parent": "home1",
        "segment": "test",
        "config": request.app.settings,
    })

@router.get("/tables", response_model=None)
@login_required(["user_auth"])
async def tables_view(request: Request):    
    return render_template(request=request, template_name="pages/tables.html", context={
        "url_for": url_for,
        "parent": "/",
        "segment": "test",
        "config": request.app.settings,
    })

@router.get("/billing", response_model=None)
@login_required(["user_auth"])
async def billing_view(request: Request):    
    return render_template(request=request, template_name="pages/billing.html", context={
        "url_for": url_for,
        "parent": "/",
        "segment": "test",
        "config": request.app.settings,
    })

@router.get("/profile", response_model=None)
@login_required(["user_auth"])
async def profile_view(request: Request):    
    return render_template(request=request, template_name="pages/profile.html", context={
        "url_for": url_for,
        "parent": "/",
        "segment": "test",
        "config": request.app.settings,
    })

@router.get("/users/edit/{user_id}", response_model=None)
@login_required(["user_auth"])
async def user_edit_view(request: Request, user_id: int):
    user = await UserModel.objects.filter(id=user_id).first()
    groups = await GroupModel.objects.all().execute()
    return render_template(request=request, template_name="admin/user_edit.html", context={
        "user": user,
        "groups": groups,
        "url_for": url_for,
        "config": request.app.settings,
    })

@router.post("/users/edit/{user_id}", response_model=None)
@login_required(["user_auth"])
async def user_edit_post(request: Request, user_id: int):
    form = await request.form()
    user = await UserModel.objects.filter(id=user_id).first()
    if user:
        user.name = form.get("name")
        user.age = int(form.get("age"))
        user.email = form.get("email")
        user.organization = form.get("organization")
        group_id = int(form.get("group_id"))
        user.group = group_id
        await user.save()
    return render_template(request=request, template_name="admin/user_edit.html", context={
        "user": user,
        "groups": await GroupModel.objects.all().execute(),
        "url_for": url_for,
        "config": request.app.settings,
        "success": True
    })

@router.get("/groups/edit/{group_id}", response_model=None)
@login_required(["user_auth"])
async def group_edit_view(request: Request, group_id: int):
    group = await GroupModel.objects.filter(id=group_id).first()
    return render_template(request=request, template_name="admin/group_edit.html", context={
        "group": group,
        "url_for": url_for,
        "config": request.app.settings,
    })

@router.post("/groups/edit/{group_id}", response_model=None)
@login_required(["user_auth"])
async def group_edit_post(request: Request, group_id: int):
    form = await request.form()
    group = await GroupModel.objects.filter(id=group_id).first()
    if group:
        group.name = form.get("name")
        group.description = form.get("description")
        await group.save()
    return render_template(request=request, template_name="admin/group_edit.html", context={
        "group": group,
        "url_for": url_for,
        "config": request.app.settings,
        "success": True
    })

# --- User Create ---
@router.get("/users/create", response_model=None)
@login_required(["user_auth"])
async def user_create_view(request: Request):
    groups = await GroupModel.objects.all().execute()
    return render_template(request=request, template_name="admin/user_create.html", context={
        "groups": groups,
        "url_for": url_for,
        "config": request.app.settings,
    })

@router.post("/users/create", response_model=None)
@login_required(["user_auth"])
async def user_create_post(request: Request):
    form = await request.form()
    user = UserModel(
        name=form.get("name"),
        age=int(form.get("age")),
        email=form.get("email"),
        password_hash="",  # Set password later or generate
        group=int(form.get("group_id")),
        organization=form.get("organization")
    )
    await user.save()
    return render_template(request=request, template_name="admin/user_create.html", context={
        "groups": await GroupModel.objects.all().execute(),
        "url_for": url_for,
        "config": request.app.settings,
        "success": True
    })

# --- User Delete ---
@router.get("/users/delete/{user_id}", response_model=None)
@login_required(["user_auth"])
async def user_delete_confirm(request: Request, user_id: int):
    user = await UserModel.objects.filter(id=user_id).first()
    return render_template(request=request, template_name="admin/user_delete.html", context={
        "user": user,
        "url_for": url_for,
        "config": request.app.settings,
    })

@router.post("/users/delete/{user_id}", response_model=None)
@login_required(["user_auth"])
async def user_delete_post(request: Request, user_id: int):
    user = await UserModel.objects.filter(id=user_id).first()
    if user:
        await user.delete()
    # Redirect to users list after deletion
    return render_template(request=request, template_name="admin/user_delete.html", context={
        "deleted": True,
        "url_for": url_for,
        "config": request.app.settings,
    })

# --- Group Create ---
@router.get("/groups/create", response_model=None)
@login_required(["user_auth"])
async def group_create_view(request: Request):
    form = GroupCreateForm()
    return render_template(request=request, template_name="admin/group_create.html", context={
        "form": form,
        "url_for": url_for,
        "config": request.app.settings,
    })

@router.post("/groups/create", response_model=None)
@login_required(["user_auth"])
async def group_create_post(request: Request):
    data = await request.form()
    form = GroupCreateForm(data)
    if form.is_valid():
        group = GroupModel(
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"]
        )
        await group.save()
        return render_template(request=request, template_name="admin/group_create.html", context={
            "form": GroupCreateForm(),
            "url_for": url_for,
            "config": request.app.settings,
            "success": True
        })
    return render_template(request=request, template_name="admin/group_create.html", context={
        "form": form,
        "url_for": url_for,
        "config": request.app.settings,
        "errors": "Please fix the errors in the form."
    })

# --- Group Delete ---
@router.get("/groups/delete/{group_id}", response_model=None)
@login_required(["user_auth"])
async def group_delete_confirm(request: Request, group_id: int):
    group = await GroupModel.objects.filter(id=group_id).first()
    return render_template(request=request, template_name="admin/group_delete.html", context={
        "group": group,
        "url_for": url_for,
        "config": request.app.settings,
    })

@router.post("/groups/delete/{group_id}", response_model=None)
@login_required(["user_auth"])
async def group_delete_post(request: Request, group_id: int):
    group = await GroupModel.objects.filter(id=group_id).first()
    if group:
        await group.delete()
    return render_template(request=request, template_name="admin/group_delete.html", context={
        "deleted": True,
        "url_for": url_for,
        "config": request.app.settings,
    })
