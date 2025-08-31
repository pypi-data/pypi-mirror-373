import bcrypt
from typing import Union
from datetime import datetime, timedelta
import jwt

try:
    from raystack.conf import settings
except ImportError:
    from config.settings import SECRET_KEY, ALGORITHM
    # Create a mock settings object
    class MockSettings:
        SECRET_KEY = SECRET_KEY
        ALGORITHM = ALGORITHM
    settings = MockSettings()


import asyncio

def asyncify(func):
    """Convert synchronous function to asynchronous."""
    async def inner(*args, **kwargs):
        try:
            # Python 3.7+
            loop = asyncio.get_running_loop()
        except AttributeError:
            # Python 3.6
            loop = asyncio.get_event_loop()
        func_out = await loop.run_in_executor(None, func, *args, **kwargs)
        return func_out
    return inner

@asyncify
def hash_password(password: str):
    """Hash password using bcrypt and return string for database storage."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

@asyncify
def check_password(password: str, hashed_pass):
    """Check password against hash. Handles both string and bytes formats."""
    if isinstance(hashed_pass, str):
        hashed_pass = hashed_pass.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed_pass)

def generate_jwt(user_id: int):
    """Generate JWT token for user authentication."""
    if user_id is None:
        return None
    
    payload = {'sub': user_id, 'exp': datetime.utcnow() + timedelta(days=1)}

    # Get settings directly from config
    try:
        from config.settings import SECRET_KEY, ALGORITHM
        secret_key = SECRET_KEY
        algorithm = ALGORITHM
    except ImportError:
        secret_key = 'default-secret-key'
        algorithm = 'HS256'

    # Use secret_key as is (keep bytes format for consistency)
    key = secret_key

    try:
        token = jwt.encode(payload, key, algorithm=algorithm)
        # PyJWT < 2 returns bytes
        if isinstance(token, (bytes, bytearray)):
            token = token.decode('utf-8')
        return token
    except Exception:
        return None