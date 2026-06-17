import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, Header

# In production, this comes from a Kubernetes Secret (mounted as env var via Helm),
# never hardcoded. See gitops repo values.yaml + sealed-secrets / external-secrets pattern.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Demo user store. Replace with real identity provider (Cognito, Auth0, etc.) in production.
_demo_users = {"admin": "admin123", "testuser": "testpass"}


def authenticate_user(username: str, password: str) -> bool:
    return _demo_users.get(username) == password


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(authorization: str = Header(...)) -> str:
    """Dependency used to protect routes — extracts and validates the Bearer token."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.removeprefix("Bearer ")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
