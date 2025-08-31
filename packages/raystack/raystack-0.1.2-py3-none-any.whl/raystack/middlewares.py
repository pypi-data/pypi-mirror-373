from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.authentication import AuthenticationBackend, SimpleUser, AuthCredentials
import jwt
from raystack.conf import settings

class JWTAuthentication(AuthenticationBackend):
    """JWT authentication for checking tokens from cookies."""
    async def authenticate(self, request):
        jwt_token = request.cookies.get("jwt")
        if not jwt_token:
            return None
        try:
            # Get settings safely
            try:
                secret_key = getattr(settings, 'SECRET_KEY', 'default-secret-key')
                algorithm = getattr(settings, 'ALGORITHM', 'HS256')
            except ImportError:
                secret_key = 'default-secret-key'
                algorithm = 'HS256'
            
            payload = jwt.decode(jwt_token, secret_key, algorithms=[algorithm])
            user_id = payload.get("sub")
            if user_id is None:
                return None
            return AuthCredentials(["user_auth", "admin"]), SimpleUser(str(user_id))
        except jwt.ExpiredSignatureError:
            return None
        except (jwt.InvalidSignatureError, jwt.InvalidTokenError, jwt.DecodeError):
            return None

class SimpleAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for authentication with JWT token verification.
    """
    def __init__(self, app):
        super().__init__(app)
        self.auth_backend = JWTAuthentication()

    async def dispatch(self, request: Request, call_next):
        # Check authentication via JWT
        auth_result = await self.auth_backend.authenticate(request)
        
        if auth_result:
            credentials, user = auth_result
            request.scope["auth"] = credentials
            request.scope["user"] = user
        else:
            # User not authenticated - create empty objects
            from starlette.authentication import AuthCredentials
            request.scope["auth"] = AuthCredentials([])  # Empty permissions
            request.scope["user"] = None
        
        response = await call_next(request)
        return response


class PermissionMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Check if this is an HTTP request
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Create Request object for convenience
        request = Request(scope, receive)

        # For test projects, allow all requests
        # In real projects, there should be actual authentication verification here
        await self.app(scope, receive, send)
        return
