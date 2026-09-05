import time
from datetime import date
import streamlit as st
from google import genai

# -----------------------------
# App Configuration & Page Title
# -----------------------------
st.set_page_config(
    page_title="MailCraft AI - Smart Email Assistant",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Custom Styling (CSS)
# -----------------------------
st.markdown("""
<style>
    /* Main Background Accent */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Title Banner Box */
    .header-box {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.4);
    }
    
    .header-title {
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 14px;
        opacity: 0.9;
        margin-top: 6px;
    }

    /* Metric Card Styling */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 12px 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .metric-value {
        font-size: 22px;
        font-weight: 700;
        color: #38bdf8;
    }
    
    .metric-label {
        font-size: 12px;
        color: #94a3b8;
    }

    /* Primary Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.6) !important;
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

# Reset counter at midnight
if st.session_state.last_reset_date != date.today():
    st.session_state.request_count = 0
    st.session_state.last_reset_date = date.today()

# -----------------------------
# Header UI & SVG Logo
# -----------------------------
st.markdown("""
<div class="header-box">
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:8px;">
        <path d="M3 8L10.8906 13.2604C11.5624 13.7083 12.4376 13.7083 13.1094 13.2604L21 8M5 19H19C20.1046 19 21 18.1046 21 17V7C21 5.89543 20.1046 5 19 5H5C3.89543 5 3 5.89543 3 7V17C3 18.1046 3.89543 19 5 19Z" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <div class="header-title">MailCraft AI Assistant</div>
    <div class="header-subtitle">Generate hyper-personalized emails, captions & hashtags instantly</div>
</div>
""", unsafe_allow_html=True)

# Top Bar Usage Dashboard
remaining = MAX_REQS = DAILY_LIMIT - st.session_state.request_count
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
        <div class="metric-value" style="color:#10b981;">{remaining}</div>
        <div class="metric-label">Remaining API Capacity</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# API Client Setup
# -----------------------------
def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("⚠️ `GEMINI_API_KEY` missing. Please add it in Streamlit Secrets.")
        st.stop()
    return genai.Client(api_key=api_key)

# -----------------------------
# User Input Section
# -----------------------------
st.subheader("⚙️ Configure Email Settings")

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
        "Communication Tone",
        ["Professional & Respectful", "Friendly & Professional", "Formal", "Warm & Respectful"]
    )

with col2:
    professional = st.text_input(
        "Business / Sender Name",
        placeholder="e.g., TechCorp Solutions"
    )
    audience = st.text_input(
        "Target Audience",
        placeholder="e.g., Enterprise Clients, HR Managers"
    )

topic = st.text_area(
    "Topic / Core Message Details *",
    placeholder="Describe what you want to communicate (e.g., Announcing a 20% discount offer for Q3 subscribers...)",
    height=120
)

generate = st.button("🚀 Generate Email Content", use_container_width=True)

# -----------------------------
# Email Generation Logic
# -----------------------------
if generate:
    if not topic.strip():
        st.warning("Please enter a topic or core message before generating.")
        st.stop()

    if st.session_state.request_count >= DAILY_LIMIT:
        st.error("❌ Daily limit of 1500 generations reached. Counter resets at midnight.")
        st.stop()

    prompt = f"""
You are an expert professional communication and social media copywriter.

Write high-converting content based on these inputs:
- Content Type: {content_type}
- Platform: {platform}
- Topic: {topic}
- Business/Person: {professional or "Not specified"}
- Tone: {tone}
- Target Audience: {audience or "General audience"}

Provide ONLY the output organized into these exact section titles:

SUBJECT:
A clear, clickable subject line or post title.

MAIN CONTENT:
The polished main body of the email or message. Keep it well-formatted with appropriate line breaks and professional sign-off.

CAPTION:
A engaging 1-2 sentence caption tailored for {platform}.

HASHTAGS:
8-10 relevant high-traffic hashtags (e.g. #Business #Communication).
"""

    client = get_client()
    models_to_try = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
    response = None
    last_error = None

    with st.spinner("✨ Crafting your content..."):
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    break
            except Exception as e:
                last_error = e
                time.sleep(1)

    if response and response.text:
        # Increment request counter
        st.session_state.request_count += 1

        st.success("🎉 Content Generated Successfully!")
        
        # Display output in stylized container
        st.text_area("Generated Content (Ready to Copy)", response.text, height=450)

        st.download_button(
            label="📥 Download Content as TXT File",
            data=response.text,
            file_name="generated_email.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.error(f"Generation failed: {last_error}. Please try clicking generate again.")

st.divider()
st.caption("Powered by Google Gemini 3.6 API | Optimized for High Throughput")
