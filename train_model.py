"""
train_model.py
==============
Trains a spam call detection model using TF-IDF + Logistic Regression.

Dataset: We generate a labelled dataset of call transcripts here for
demonstration. In production, replace with a real dataset (see README for
suggestions). The model is saved as `spam_model.pkl` and the vectorizer as
`tfidf_vectorizer.pkl`.

Run:
    python train_model.py
"""

import os
import re
import json
import joblib
import numpy as np
import pandas as pd
import nltk

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix
)
from sklearn.pipeline import Pipeline
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# ─────────────────────────────────────────────
# 1. Download required NLTK resources
# ─────────────────────────────────────────────
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("punkt_tab", quiet=True)

# ─────────────────────────────────────────────
# 2. Sample dataset (replace with real data)
# ─────────────────────────────────────────────
SPAM_SAMPLES = [
    "Congratulations! You have won a lottery of $1,000,000. Call us now to claim your prize.",
    "Your bank account has been compromised. Verify your details immediately by pressing 1.",
    "This is the IRS. You owe back taxes. Pay now or face arrest within 24 hours.",
    "Your credit card has been charged $500. Call immediately to dispute this charge.",
    "You have been selected for a free vacation package. Provide your credit card to confirm.",
    "Your social security number has been suspended. Press 1 to speak with an agent.",
    "We are calling about your car's extended warranty. It's about to expire.",
    "You qualify for a $5000 government grant. No repayment required. Claim now.",
    "Your account will be terminated unless you verify your information immediately.",
    "Hello, this is Amazon. There is a suspicious login on your account. Press 1 now.",
    "Urgent: Your PayPal account has been limited. Log in now to restore access.",
    "Final notice: Legal action will be taken unless you pay the outstanding amount today.",
    "You have been pre-approved for a low-interest loan. Call now to accept.",
    "Your Medicare benefits are expiring. Call to renew and receive free supplies.",
    "This is a notice from the Social Security Administration regarding your benefits.",
    "Your computer is infected with a virus. Call Microsoft support immediately.",
    "Press 1 to claim your free cruise vacation. Limited time offer.",
    "You owe money to the government. Failure to pay will result in your arrest.",
    "Your identity has been stolen. Please verify your details to protect yourself.",
    "Call back immediately. This is your last chance to avoid legal consequences.",
    "We are from the bank fraud department. Your card was used in another city.",
    "Congratulations, you have been selected for our exclusive reward program.",
    "Your investment account has flagged unusual activity. Call now to secure funds.",
    "This is a final warning regarding your unpaid debt. Contact us immediately.",
    "You have won a prize in our sweepstakes. Provide your bank details to receive it.",
    "Your phone service will be disconnected today unless you pay the overdue balance.",
    "Hello, we are conducting a survey and offering a free gift card as a reward.",
    "We noticed a large transaction on your account. Press 2 to cancel this transfer.",
    "Your insurance policy has lapsed. Call now to avoid losing your coverage.",
    "Special offer: Refinance your mortgage and save thousands. Call now.",
    "This is a call from the debt collection agency. Pay now to avoid court.",
    "We have detected fraud on your debit card. Call now to freeze the card.",
    "Your subscription has been auto-renewed for $199. Press 1 to cancel.",
    "You are eligible for a student loan forgiveness program. Act immediately.",
    "Police arrest warrant has been issued in your name. Call now to resolve.",
]

SAFE_SAMPLES = [
    "Hi, this is Dr. Smith's office calling to confirm your appointment tomorrow at 2 PM.",
    "Hello, I'm calling from the library to let you know your reserved book is available.",
    "This is a reminder that your dental cleaning is scheduled for next Tuesday.",
    "Hi, I'm calling to follow up on the job application you submitted last week.",
    "Your package has been delivered to your front door. Please confirm receipt.",
    "This is the school calling to inform you that school will be closed tomorrow.",
    "Hello, your prescription is ready for pickup at the pharmacy.",
    "I'm calling to confirm your restaurant reservation for 7 PM tonight.",
    "Hi, this is your landlord calling about the maintenance request you submitted.",
    "We're calling to remind you about your car service appointment tomorrow morning.",
    "Hello, your test results are back. The doctor would like to discuss them with you.",
    "This is a courtesy call to let you know your order has shipped.",
    "Hi, I'm calling from the vet's office to check on your pet after the procedure.",
    "Your internet service will be temporarily down for maintenance tonight from 2 to 4 AM.",
    "Hello, your dry cleaning is ready to be picked up at the store.",
    "This is a reminder from your gym that your membership renewal is due next week.",
    "Hi, I'm calling to schedule a free home inspection at your convenience.",
    "Your ride is arriving in 3 minutes. Your driver's name is John.",
    "Hello, this is customer support. I'm calling back regarding your recent inquiry.",
    "Your grocery order is out for delivery and will arrive within the hour.",
    "Hi, I wanted to touch base about the project proposal we discussed last week.",
    "This is the HR department calling about your onboarding schedule next Monday.",
    "Hello, the part for your appliance has arrived. We can schedule the repair now.",
    "I'm calling to let you know your parking permit application has been approved.",
    "Hi, this is a courtesy reminder about your mortgage payment due next Friday.",
    "Your blood donation appointment is confirmed for Saturday at 10 AM.",
    "Hello, this is the city utilities office regarding your service transfer request.",
    "I'm calling to schedule the annual pest control treatment for your home.",
    "Your visa application status has been updated. Please check the portal.",
    "Hi, this is the property manager calling about the lease renewal documents.",
    "Hello, I wanted to confirm that your refund has been processed successfully.",
    "Your flight has been rescheduled. Please check your email for new details.",
    "This is a reminder that your tax documents are ready for review.",
    "Hi, calling to let you know the estimate for your home repair is ready.",
    "Your appointment with the financial advisor is confirmed for Thursday at 3 PM.",
]

# ─────────────────────────────────────────────
# 3. Build DataFrame
# ─────────────────────────────────────────────
def build_dataset() -> pd.DataFrame:
    texts  = SPAM_SAMPLES + SAFE_SAMPLES
    labels = [1] * len(SPAM_SAMPLES) + [0] * len(SAFE_SAMPLES)   # 1=spam, 0=safe
    df = pd.DataFrame({"text": texts, "label": labels})
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df

# ─────────────────────────────────────────────
# 4. Text preprocessing
# ─────────────────────────────────────────────
stemmer   = PorterStemmer()
stop_words = set(stopwords.words("english"))

# Words that strongly indicate spam – kept even after stopword removal
SPAM_KEYWORDS = {
    "arrest", "warrant", "irs", "tax", "fraud", "account", "credit",
    "debit", "bank", "verify", "claim", "prize", "lottery", "free",
    "win", "won", "suspend", "terminate", "legal", "immediate",
    "urgently", "urgent", "press", "limited", "expire", "grant",
    "bitcoin", "crypto", "wire", "transfer", "refund", "lucky",
    "congratulations", "selected", "eligible", "lawsuit", "overdue",
}


def preprocess(text: str) -> str:
    """
    Lowercase → remove special chars → tokenise →
    remove stopwords (keep spam keywords) → stem.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = word_tokenize(text)
    tokens = [
        stemmer.stem(t)
        for t in tokens
        if t not in stop_words or t in SPAM_KEYWORDS
    ]
    return " ".join(tokens)


# ─────────────────────────────────────────────
# 5. Train
# ─────────────────────────────────────────────
def train():
    print("=" * 55)
    print("  AI Call Spam Detector – Model Training")
    print("=" * 55)

    df = build_dataset()
    print(f"\nDataset: {len(df)} samples  |  Spam: {df['label'].sum()}  |  Safe: {(df['label']==0).sum()}")

    # Preprocess
    df["clean_text"] = df["text"].apply(preprocess)

    X_train, X_test, y_train, y_test = train_test_split(
        df["clean_text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    # Pipeline: TF-IDF + Logistic Regression
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),   # unigrams + bigrams
            max_features=5000,
            sublinear_tf=True,    # log-scaled TF
        )),
        ("clf", LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        )),
    ])

    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    print("\n── Evaluation Metrics ──────────────────────────")
    print(f"  Accuracy  : {accuracy_score(y_test, y_pred):.4f}")
    print(f"  Precision : {precision_score(y_test, y_pred):.4f}")
    print(f"  Recall    : {recall_score(y_test, y_pred):.4f}")
    print(f"  F1-Score  : {f1_score(y_test, y_pred):.4f}")
    print("\n── Classification Report ───────────────────────")
    print(classification_report(y_test, y_pred, target_names=["Safe", "Spam"]))
    print("── Confusion Matrix ────────────────────────────")
    print(confusion_matrix(y_test, y_pred))

    # Save model + vectorizer
    os.makedirs("models", exist_ok=True)
    joblib.dump(pipeline, "models/spam_model.pkl")

    # Save metrics
    metrics = {
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall":    round(recall_score(y_test, y_pred), 4),
        "f1_score":  round(f1_score(y_test, y_pred), 4),
    }
    with open("models/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    # Save suspicious keywords list for frontend highlighting
    with open("models/spam_keywords.json", "w") as f:
        json.dump(sorted(SPAM_KEYWORDS), f, indent=2)

    print("\n✅  Model saved  →  backend/models/spam_model.pkl")
    print("✅  Metrics saved →  backend/models/metrics.json")
    print("✅  Keywords saved → backend/models/spam_keywords.json")
    return pipeline


if __name__ == "__main__":
    train()
