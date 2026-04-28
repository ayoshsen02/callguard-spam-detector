# 🛡️ CallGuard – AI-Based Call Spam Detection System

A full-stack AIML project that uses **NLP + Logistic Regression** to classify call transcripts as **SAFE** or **SPAM/FRAUD** in real time, with a modern React dashboard.

---

## 📁 Folder Structure

```
spam-detector/
├── backend/
│   ├── main.py                  ← FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── models/                  ← auto-created after training
│   │   ├── spam_model.pkl
│   │   ├── metrics.json
│   │   └── spam_keywords.json
│   ├── ml/
│   │   ├── train_model.py       ← dataset generation + model training
│   │   └── predictor.py         ← inference wrapper used by API
│   ├── routes/
│   │   ├── analyze.py           ← POST /api/analyze
│   │   ├── auth.py              ← POST /api/auth/send-otp, /verify-otp
│   │   └── history.py           ← GET/DELETE /api/history
│   └── utils/
│       ├── firebase.py          ← Firebase Admin SDK init (stub-safe)
│       ├── jwt_handler.py       ← JWT sign / verify
│       └── auth_guard.py        ← FastAPI auth dependency
│
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── tailwind.config.js
    ├── .env.example
    └── src/
        ├── App.jsx              ← routing + auth context
        ├── main.jsx
        ├── pages/
        │   ├── LoginPage.jsx    ← phone + OTP login
        │   ├── Dashboard.jsx    ← main analysis UI
        │   └── HistoryPage.jsx  ← per-user history
        ├── components/
        │   ├── Navbar.jsx
        │   ├── ResultCard.jsx   ← verdict + confidence display
        │   └── HighlightedText.jsx ← suspicious word highlighting
        ├── utils/
        │   ├── api.js           ← axios API client
        │   └── firebase.js      ← Firebase JS SDK helpers
        └── styles/
            └── index.css
```

---

## 🤖 ML Pipeline

### Dataset
The demo uses 70 labelled call transcripts (35 spam, 35 safe) defined inline in
`train_model.py`. For a real production system, use:

| Dataset | Source |
|---------|--------|
| SMS Spam Collection | [UCI ML Repository](https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection) |
| FraudBuster Transcripts | Kaggle – search "call center fraud transcripts" |
| Robocall Scripts | FTC Consumer Sentinel / TRACED Act disclosures |
| Synthetic expansion | Use GPT-4 to generate more labelled examples |

### Preprocessing Pipeline
```
Raw text
  → lowercase
  → remove special characters / numbers
  → NLTK word_tokenize
  → remove stopwords  (but keep spam-specific keywords like "arrest", "irs", "warrant")
  → PorterStemmer
  → cleaned string
```

### Model: TF-IDF + Logistic Regression (Scikit-learn Pipeline)
```
TfidfVectorizer(ngram_range=(1,2), max_features=5000, sublinear_tf=True)
       +
LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000)
```

**Why this model?**
- Fast to train and serve (< 1 ms inference)
- Handles class imbalance (`class_weight="balanced"`)
- Bigrams capture phrases like "press 1", "back taxes", "legal action"
- Easily interpretable – you can inspect feature weights
- Baseline F1 ≈ 0.92–0.96 on the demo dataset

### Evaluation Metrics (example output)
```
Accuracy  : 0.9286
Precision : 0.9333
Recall    : 0.9333
F1-Score  : 0.9333

              precision  recall  f1-score   support
        Safe       0.93    0.93      0.93         7
        Spam       0.93    0.93      0.93         7
```

### Advanced Models (Optional Upgrade Path)
| Model | When to use | How |
|-------|-------------|-----|
| **LSTM** | Large dataset (10k+ samples) | `tensorflow.keras` Sequential → Embedding → LSTM → Dense |
| **DistilBERT** | Best accuracy, GPU available | `transformers` – `pipeline("text-classification")` |
| **Rule-based boost** | Instant win | Add keyword score on top of ML probability |

---

## 🚀 Running the Project Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- VS Code (recommended)

---

### Step 1 – Clone & Open in VS Code
```bash
cd spam-detector
code .
```

---

### Step 2 – Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env file
cp .env.example .env
# (edit .env if you have Firebase credentials)
```

---

### Step 3 – Train the ML Model
```bash
# Still inside backend/ with venv active
python ml/train_model.py
```
Expected output:
```
Dataset: 70 samples  |  Spam: 35  |  Safe: 35
── Evaluation Metrics ──────────────────────────
  Accuracy  : 0.9286
  F1-Score  : 0.9333
✅  Model saved  →  backend/models/spam_model.pkl
```

---

### Step 4 – Start the Backend Server
```bash
uvicorn main:app --reload --port 8000
```
The API is now live at `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

---

### Step 5 – Frontend Setup
Open a **new terminal**:
```bash
cd frontend

# Install dependencies
npm install

# Copy env file
cp .env.example .env
# (add Firebase config values if you have them)

# Start dev server
npm run dev
```
Frontend: `http://localhost:3000`

---

### Step 6 – Use the App (Dev Mode)
1. Open `http://localhost:3000`
2. Enter **any phone number** (e.g. `+919876543210`) → click **Send OTP**
3. Enter **any 6 digits** (e.g. `123456`) → click **Verify & Sign In**
4. On the Dashboard, click **Sample Spam** or **Sample Safe** to auto-fill a transcript
5. Click **Analyse Call** and see the result with confidence score and highlights

> Dev mode is enabled by default (`DEV_MODE=true` in backend `.env` and  
> `const DEV_MODE = true` in `LoginPage.jsx`). No Firebase needed.

---

## 🔥 Firebase Setup (Optional – for real auth + history)

1. Go to [Firebase Console](https://console.firebase.google.com) → Create project
2. Enable **Phone Authentication** under Authentication → Sign-in methods
3. Add a **Web App** → copy config → paste into `frontend/.env`
4. Create a **Firestore database** (start in test mode)
5. Go to Project Settings → Service Accounts → Generate new private key
6. Save as `backend/serviceAccountKey.json`
7. In `backend/.env`: set `FIREBASE_CREDENTIALS=serviceAccountKey.json`
8. In `frontend/src/pages/LoginPage.jsx`: set `const DEV_MODE = false`
9. In `backend/.env`: set `DEV_MODE=false`

---

## 🔌 API Reference

### `POST /api/analyze`
```json
Request:  { "text": "This is the IRS calling..." }
Response: {
  "id": "uuid",
  "label": "spam",
  "confidence": 0.9421,
  "spam_probability": 0.9421,
  "safe_probability": 0.0579,
  "suspicious_words": ["irs", "arrest", "warrant"],
  "timestamp": "2025-01-01T12:00:00+00:00"
}
```

### `POST /api/auth/verify-otp`
```json
Request:  { "id_token": "<firebase-id-token>" }
Response: { "token": "<jwt>", "uid": "<uid>" }
```

### `GET /api/history?limit=20`
```json
Response: { "history": [...], "total": 5 }
```

### `DELETE /api/history/{id}`
```json
Response: { "message": "Deleted successfully." }
```

All endpoints except `/api/auth/*` require:
```
Authorization: Bearer <jwt>
```

---

## 🌐 Deployment Guide

### Backend → Render
1. Push to GitHub
2. New Web Service on [render.com](https://render.com)
3. Build command: `pip install -r requirements.txt && python ml/train_model.py`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env`

### Frontend → Vercel
1. Push `frontend/` to GitHub
2. Import on [vercel.com](https://vercel.com)
3. Add environment variables from `.env`
4. Set `VITE_API_BASE_URL` to your Render backend URL
5. Update Vite proxy in `vite.config.js` to use the env variable in production

### Alternative: Railway (full-stack on one platform)
Railway supports both Python and Node on the same project.
See: [railway.app](https://railway.app)

---

## 💡 Production Improvements

| Area | Suggestion |
|------|-----------|
| **Data** | Collect real call transcripts via user-submitted reports; label with a human review queue |
| **Model** | Fine-tune DistilBERT on 10k+ real examples for 5–10% F1 improvement |
| **Real-time** | Stream audio → Whisper transcription → live spam score |
| **Rate limiting** | Add `slowapi` to FastAPI; limit to 20 analyses/hour per user |
| **Feedback loop** | "Was this correct?" button → store corrections → retrain weekly |
| **Explainability** | Use LIME/SHAP to highlight *why* a call was flagged |
| **Languages** | Add multilingual support via `paraphrase-multilingual-MiniLM` |
| **Monitoring** | Grafana + Prometheus for API latency and prediction drift |

---

## 🔒 Data Collection (Safely & Ethically)

- **Never record real calls without consent** – illegal in most jurisdictions
- Use **publicly available** FTC/FCC robocall complaint datasets
- Implement **data anonymisation** before storage (strip phone numbers, names)
- Add a clear **privacy policy** and **terms of service**
- Comply with **PDPB (India)**, GDPR (EU), or CCPA (USA) as applicable

---

## 📦 Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend  | FastAPI + Uvicorn |
| ML Model | Scikit-learn (TF-IDF + Logistic Regression) |
| Auth     | Firebase Phone Auth (OTP) + JWT |
| Database | Firebase Firestore |
| Fonts    | Syne + DM Sans + JetBrains Mono |
| Deploy   | Vercel (frontend) + Render (backend) |
