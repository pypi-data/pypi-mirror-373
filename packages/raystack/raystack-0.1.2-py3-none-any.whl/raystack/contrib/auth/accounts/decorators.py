from functools import wraps
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.authentication import has_required_scope


def login_required(required_scopes=None):
    """
    Decorator for authentication check.
    If user is not authenticated, redirects to login page.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Check if user has required permissions
            if not has_required_scope(request, required_scopes or []):
                # Redirect to login page
                return RedirectResponse(url="/accounts/login", status_code=303)
            
            # If all checks passed, call the original function
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator

