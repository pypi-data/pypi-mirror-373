from typing import Optional, Union, Any
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel

class TokenPayload(BaseModel):
    sub: Optional[int] = None

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    # Get settings safely
    try:
        from raystack.conf import settings
        secret_key = getattr(settings, 'SECRET_KEY', 'default-secret-key')
        algorithm = getattr(settings, 'ALGORITHM', 'HS256')
        default_expire_minutes = getattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', 30)
    except ImportError:
        secret_key = 'default-secret-key'
        algorithm = 'HS256'
        default_expire_minutes = 30

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=default_expire_minutes)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt