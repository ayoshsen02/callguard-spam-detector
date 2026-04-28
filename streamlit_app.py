"""
streamlit_app.py — CallGuard Spam Detector
"""
import sys
import os
import re
import nltk

# Download NLTK data (needed on Streamlit Cloud)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

import streamlit as st
from ml.predictor import predict

# ── Custom CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main { background-color: #060d18; }
.stTextArea textarea {
    background-color: #0d1f35 !important;
    color: #e8f4fd !important;
    border: 1px solid rgba(56,189,248,0.2) !important;
    border-radius: 10px !important;
}
.spam-box {
    background: rgba(239,68,68,0.1);
    border: 2px solid rgba(239,68,68,0.4);
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
}
.safe-box {
    background: rgba(34,197,94,0.1);
    border: 2px solid rgba(34,197,94,0.4);
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
}
.keyword-badge {
    background: rgba(245,158,11,0.15);
    border: 1px solid rgba(245,158,11,0.4);
    border-radius: 6px;
    padding: 2px 10px;
    color: #fbbf24;
    font-family: monospace;
    font-size: 13px;
    margin: 3px;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────
st.markdown("# 🛡️ CallGuard")
st.markdown("### AI-Powered Call Spam Detection System")
st.markdown("Paste a call transcript below. The AI will instantly detect if it's **safe** or **spam/fraud**.")
st.divider()

# ── Sample buttons ────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

SAMPLE_SPAM = "This is the IRS calling. A warrant has been issued in your name for unpaid taxes. You must pay $3,200 immediately or face arrest within 24 hours. Press 1 now to speak with an agent."
SAMPLE_SAFE = "Hi, this is Dr. Smith's office calling to confirm your appointment tomorrow at 2 PM. Please call us back at 555-0100 if you need to reschedule. Have a great day!"

if col1.button("⚠️ Load Sample SPAM", use_container_width=True):
    st.session_state["transcript"] = SAMPLE_SPAM

if col2.button("✅ Load Sample SAFE", use_container_width=True):
    st.session_state["transcript"] = SAMPLE_SAFE

# ── Text input ────────────────────────────────────────────────────────────
transcript = st.text_area(
    "📞 Call Transcript",
    value=st.session_state.get("transcript", ""),
    height=180,
    placeholder="Paste or type the call conversation here…\n\nExample: 'Hello, this is the IRS calling about unpaid taxes…'",
    max_chars=5000,
)

char_count = len(transcript)
st.caption(f"{char_count} / 5000 characters")

# ── Analyse button ────────────────────────────────────────────────────────
if st.button("🔍 Analyse Call", type="primary", use_container_width=True):
    if char_count < 10:
        st.warning("⚠️ Please enter at least 10 characters.")
    else:
        with st.spinner("🤖 AI is analysing the call..."):
            try:
                result = predict(transcript)
            except FileNotFoundError:
                st.error("❌ Model not found. Make sure `backend/models/spam_model.pkl` exists.")
                st.info("Run: `cd backend && python ml/train_model.py`")
                st.stop()
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.stop()

        is_spam = result["label"] == "spam"
        confidence = int(result["confidence"] * 100)
        spam_pct = int(result["spam_probability"] * 100)
        safe_pct = int(result["safe_probability"] * 100)

        st.divider()

        # ── Verdict ──────────────────────────────────────────────────────
        if is_spam:
            st.markdown(f"""
            <div class="spam-box">
                <h2 style="color:#f87171;margin:0">⚠️ SPAM / FRAUD CALL</h2>
                <p style="color:#fca5a5;margin:8px 0 0">
                    Do not share personal information. This call shows strong fraud indicators.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="safe-box">
                <h2 style="color:#4ade80;margin:0">✅ SAFE CALL</h2>
                <p style="color:#86efac;margin:8px 0 0">
                    No significant spam signals detected. This call appears legitimate.
                </p>
            </div>
            """, unsafe_allow_html=True)

        # ── Confidence bar ────────────────────────────────────────────────
        st.markdown("#### 📊 Confidence Score")
        st.progress(result["confidence"])
        st.markdown(f"**{confidence}% confident** this is a **{result['label'].upper()}** call")

        # ── Metrics ───────────────────────────────────────────────────────
        st.markdown("#### 📈 Probability Breakdown")
        m1, m2, m3 = st.columns(3)
        m1.metric("🏷️ Verdict",          result["label"].upper())
        m2.metric("🚨 Spam probability", f"{spam_pct}%")
        m3.metric("✅ Safe probability", f"{safe_pct}%")

        # ── Suspicious words ──────────────────────────────────────────────
        if result["suspicious_words"]:
            st.markdown("#### 🚨 Suspicious Keywords Detected")
            badges = " ".join([
                f'<span class="keyword-badge">{w}</span>'
                for w in result["suspicious_words"]
            ])
            st.markdown(badges, unsafe_allow_html=True)

            # Highlighted transcript
            st.markdown("#### 🔦 Highlighted Transcript")
            highlighted = transcript
            for word in result["suspicious_words"]:
                highlighted = re.sub(
                    rf"\b({re.escape(word)})\b",
                    r"**:orange[\1]**",
                    highlighted,
                    flags=re.IGNORECASE,
                )
            st.markdown(highlighted)
        else:
            st.info("✅ No suspicious keywords found in this transcript.")

# ── Footer ────────────────────────────────────────────────────────────────
st.divider()
st.caption("🛡️ CallGuard | Built with Scikit-learn + FastAPI + Streamlit | AI-Based Call Spam Detection")
