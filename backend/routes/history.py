from fastapi import APIRouter, Depends
from utils.auth_guard import get_current_user

router = APIRouter()

@router.get("")
async def get_history(user: dict = Depends(get_current_user)):
    return {"history": [], "total": 0}

@router.delete("/{record_id}")
async def delete_record(record_id: str, user: dict = Depends(get_current_user)):
    return {"message": "Deleted (dev mode)"}