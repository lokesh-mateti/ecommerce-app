import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

_demo_users = {"admin": "admin123", "testuser": "testpass"}


def authenticate_user(username: str, password: str) -> bool:
    return _demo_users.get(username) == password


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> str:
    """Decodes and validates a raw JWT token string. Returns username."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def verify_token(token: str) -> str:
    """Accepts a raw token string (from HTTPBearer credentials)."""
    return _decode_token(token)
