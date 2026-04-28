from fastapi import APIRouter
from pydantic import BaseModel
from utils.jwt_handler import create_token

router = APIRouter()

class VerifyOTPRequest(BaseModel):
    id_token: str

@router.post("/verify-otp")
async def verify_otp(body: VerifyOTPRequest):
    # Dev mode: accept any token
    token = create_token({"uid": "demo-user", "phone": "demo"})
    return {"token": token, "uid": "demo-user"}

@router.post("/send-otp")
async def send_otp():
    return {"message": "Dev mode — OTP not required"}