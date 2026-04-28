"""
main.py  –  FastAPI entry-point
================================
Run with:
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import analyze, auth, history

app = FastAPI(
    title="AI Call Spam Detector API",
    version="1.0.0",
    description="Detects spam/fraud calls from conversation transcripts.",
)

# ── CORS (allow React dev server) ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(auth.router,    prefix="/api/auth",    tags=["Auth"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["Analyze"])
app.include_router(history.router, prefix="/api/history", tags=["History"])


@app.get("/")
def root():
    return {"message": "AI Call Spam Detector API is running ✅"}


@app.get("/health")
def health():
    return {"status": "ok"}
