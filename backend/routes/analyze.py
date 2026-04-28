"""
routes/analyze.py
=================
POST /api/analyze  –  run spam detection on a call transcript.
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ml.predictor import predict
from utils.firebase import db          # Firestore client (stub-safe)
from utils.auth_guard import get_current_user

router = APIRouter()


# ── Request / Response schemas ─────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000,
                      description="Call conversation transcript to analyse.")


class AnalyzeResponse(BaseModel):
    id:               str
    label:            str          # "spam" | "safe"
    confidence:       float
    spam_probability: float
    safe_probability: float
    suspicious_words: list[str]
    timestamp:        str


# ── Endpoint ───────────────────────────────────────────────────────────────

@router.post("", response_model=AnalyzeResponse)
async def analyze_call(
    body: AnalyzeRequest,
    user: dict = Depends(get_current_user),
):
    """
    Analyses the supplied call transcript and returns a spam/safe prediction.
    Stores the result in Firestore under the authenticated user's history.
    """
    try:
        result = predict(body.text)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    record_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    # Persist to Firestore (skipped gracefully if Firebase not configured)
    if db is not None:
        try:
            db.collection("call_history").document(record_id).set({
                "user_id":          user["uid"],
                "text":             body.text,
                "timestamp":        timestamp,
                **result,
            })
        except Exception:
            pass  # Non-fatal – don't fail the response if DB write fails

    return AnalyzeResponse(id=record_id, timestamp=timestamp, **result)
