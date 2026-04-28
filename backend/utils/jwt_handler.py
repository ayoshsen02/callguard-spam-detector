import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

SECRET_KEY = "change-me-super-secret-key-123"
ALGORITHM  = "HS256"

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=24)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError(f"Invalid token: {exc}")