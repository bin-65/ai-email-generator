import time
from datetime import date
import streamlit as st
from google import genai

# -----------------------------
# App Configuration & Page Title
# -----------------------------
st.set_page_config(
    page_title="MailCraft AI - Smart Email Assistant",
    page_icon="✉️",
    layout="centered"
)

# -----------------------------
# Light Theme Custom CSS
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    .header-box {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
        padding: 24px;
        border-radius: 12px;
        color: #ffffff;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        font-size: 26px;
        font-weight: 800;
        margin: 0;
        color: #ffffff !important;
    }
    
    .header-subtitle {
        font-size: 14px;
        opacity: 0.95;
        margin-top: 4px;
        color: #f1f5f9 !important;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .metric-value {
        font-size: 22px;
        font-weight: 800;
        color: #1e293b;
    }
    
    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
    }

    .form-header {
        color: #0f172a;
        font-size: 18px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .stButton>button {
        background: #2563eb !important;
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
    }
    
    .stButton>button:hover {
        background: #1d4ed8 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Rate Limiter & Session State
# -----------------------------
DAILY_LIMIT = 1500

if "request_count" not in st.session_state:
    st.session_state.request_count = 0
if "last_reset_date" not in st.session_state:
    st.session_state.last_reset_date = date.today()

if st.session_state.last_reset_date != date.today():
    st.session_state.request_count = 0
    st.session_state.last_reset_date = date.today()

# -----------------------------
# App Header with SVG Logo
# -----------------------------
st.markdown("""
<div class="header-box">
    <svg width="42" height="42" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:6px;">
        <path d="M3 8L10.8906 13.2604C11.5624 13.7083 12.4376 13.7083 13.1094 13.2604L21 8M5 19H19C20.1046 19 21 18.1046 21 17V7C21 5.89543 20.1046 5 19 5H5C3.89543 5 3 5.89543 3 7V17C3 18.1046 3.89543 19 5 19Z" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <div class="header-title">MailCraft AI Assistant</div>
    <div class="header-subtitle">Generate professional emails, captions & hashtags instantly</div>
</div>
""", unsafe_allow_html=True)

# Usage Dashboard
remaining = DAILY_LIMIT - st.session_state.request_count
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{st.session_state.request_count} / {DAILY_LIMIT}</div>
        <div class="metric-label">Emails Generated Today</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color:#059669;">{remaining}</div>
        <div class="metric-label">Remaining Capacity</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# API Client
# -----------------------------
def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY is missing in Streamlit Secrets.")
        st.stop()
    return genai.Client(api_key=api_key)

# -----------------------------
# Form Inputs
# -----------------------------
st.markdown('<div class="form-header">⚙️ Email & Content Parameters</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    content_type = st.selectbox(
        "Content Type",
        ["Email", "Announcement", "Promotional Post", "Professional Update", "Thank You Message"]
    )
    platform = st.selectbox(
        "Platform",
        ["Email", "LinkedIn", "Facebook", "Instagram", "General"]
    )
    tone = st.selectbox(
        "Tone",
        ["Professional & Respectful", "Friendly & Professional", "Formal", "Warm & Respectful"]
    )

with col2:
    professional = st.text_input(
        "Business / Sender Name",
        placeholder="e.g., ABC Solutions"
    )
    audience = st.text_input(
        "Target Audience (optional)",
        placeholder="e.g., Students, HR managers"
    )

topic = st.text_area(
    "Topic / Key Details *",
    placeholder="e.g., Announcing a new AI course starting next week...",
    height=110
)

generate = st.button("✨ Generate Content", use_container_width=True)

# -----------------------------
# Content Generation
# -----------------------------
if generate:
    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    if st.session_state.request_count >= DAILY_LIMIT:
        st.error("❌ Daily limit of 1500 generations reached.")
        st.stop()

    prompt = f"""
You are an expert professional communication writer.

Generate content based on these details:
- Content Type: {content_type}
- Platform: {platform}
- Topic: {topic}
- Sender/Business: {professional or "Not specified"}
- Tone: {tone}
- Target Audience: {audience or "General"}

STRICT FORMAT REQUIREMENTS:
Format all section headers using markdown bold so they stand out clearly.

**SUBJECT:**
[Provide a clear subject line or post title here]

**MAIN CONTENT:**
[Provide the complete, well-formatted email body with clear paragraphs and a professional sign-off]

**CAPTION:**
[Provide a short 1-2 sentence caption for {platform}]

**HASHTAGS:**
[Provide 8-10 relevant hashtags starting with #]
"""

    client = get_client()
    
    # Updated reliable model list for Google Gen AI SDK
    primary_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-latest"]
    response = None
    last_error = None

    with st.spinner("⚡ Fast-generating your email..."):
        for model_name in primary_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    break
            except Exception as e:
                last_error = e
                continue

    if response and response.text:
        st.session_state.request_count += 1
        st.success("🎉 Content generated successfully!")
        
        # Formatted markdown output with bold headers
        st.markdown(response.text)
        st.divider()

        st.download_button(
            label="⬇️ Download Output as TXT",
            data=response.text,
            file_name="generated_email.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.error(f"Generation failed: {last_error}. Please re-check your API key in Streamlit Secrets.")

st.divider()
st.caption("Powered by Google Gemini API + Streamlit")
