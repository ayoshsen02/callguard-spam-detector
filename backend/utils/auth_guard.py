import os
from fastapi import Header, HTTPException
from utils.jwt_handler import decode_token

DEV_MODE = True  # Set False when you add real auth

async def get_current_user(authorization: str = Header(default="")) -> dict:
    if not authorization:
        if DEV_MODE:
            return {"uid": "demo-user", "phone": "demo"}
        raise HTTPException(status_code=401, detail="Authorization header missing.")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header.")
    try:
        return decode_token(parts[1])
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))