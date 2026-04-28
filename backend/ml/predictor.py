"""
predictor.py
============
Loads the trained pipeline and exposes a predict() function used by the API.
"""

import re
import json
import joblib
import nltk
from pathlib import Path
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

nltk.download("punkt",     quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("punkt_tab", quiet=True)

BASE_DIR   = Path(__file__).parent.parent  # backend/
MODEL_PATH = BASE_DIR / "models" / "spam_model.pkl"
KW_PATH    = BASE_DIR / "models" / "spam_keywords.json"

stemmer    = PorterStemmer()
stop_words = set(stopwords.words("english"))

# Load model once at import time
_pipeline        = None
_spam_keywords   = []


def _load_model():
    global _pipeline, _spam_keywords
    if _pipeline is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Run `python ml/train_model.py` first."
            )
        _pipeline = joblib.load(MODEL_PATH)
        if KW_PATH.exists():
            with open(KW_PATH) as f:
                _spam_keywords = json.load(f)
    return _pipeline, _spam_keywords


def preprocess(text: str) -> str:
    """Mirror of train_model.preprocess – must stay in sync."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = word_tokenize(text)
    tokens = [
        stemmer.stem(t)
        for t in tokens
        if t not in stop_words or t in _spam_keywords
    ]
    return " ".join(tokens)


def find_suspicious_words(text: str, keywords: list[str]) -> list[str]:
    """Return words in the text that match the spam keyword list."""
    words_lower = set(re.findall(r"\b\w+\b", text.lower()))
    return sorted(words_lower & set(keywords))


def predict(text: str) -> dict:
    """
    Returns:
        {
            "label":            "spam" | "safe",
            "confidence":       float (0-1),
            "spam_probability": float,
            "safe_probability": float,
            "suspicious_words": list[str],
        }
    """
    pipeline, spam_keywords = _load_model()

    clean = preprocess(text)
    proba = pipeline.predict_proba([clean])[0]   # [P(safe), P(spam)]
    spam_prob = float(proba[1])
    safe_prob = float(proba[0])

    label      = "spam" if spam_prob >= 0.5 else "safe"
    confidence = spam_prob if label == "spam" else safe_prob

    suspicious = find_suspicious_words(text, spam_keywords)

    return {
        "label":            label,
        "confidence":       round(confidence, 4),
        "spam_probability": round(spam_prob, 4),
        "safe_probability": round(safe_prob, 4),
        "suspicious_words": suspicious,
    }
