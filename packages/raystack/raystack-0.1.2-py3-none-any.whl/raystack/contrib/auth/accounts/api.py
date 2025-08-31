from fastapi import APIRouter, Request
from starlette.responses import JSONResponse, RedirectResponse
from raystack.contrib.auth.users.models import UserModel
from raystack.contrib.auth.users.utils import check_password, generate_jwt

router = APIRouter()

@router.post("/login")
async def login_user(request: Request):
    # Get form data
    form = await request.form()
    username = form.get("email")
    password = form.get("password")
    
    # Check that all fields are filled
    if not username or not password:
        return RedirectResponse("/accounts/login?error=missing_fields", status_code=303)

    # Find user
    user = await UserModel.objects.filter(email=username).first()  # type: ignore
    if not user:
        return RedirectResponse("/accounts/login?error=invalid_credentials", status_code=303)

    # Check password
    hashed_pass = user.password_hash
    valid_pass = await check_password(password, hashed_pass)
    if not valid_pass:
        return RedirectResponse("/accounts/login?error=invalid_credentials", status_code=303)

    # If all checks pass, create JWT token and redirect to admin
    response = RedirectResponse("/admin/", status_code=303)
    response.set_cookie('jwt', generate_jwt(user.id), httponly=True, path="/")
    return response

@router.post("/logout")
async def logout(request: Request):
    # Create response with redirect to login page
    response = RedirectResponse(url="/accounts/login", status_code=303)
    
    # Clear JWT token
    response.delete_cookie("jwt", path="/")
    
    # Also clear other possible tokens
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    
    return response 