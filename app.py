import streamlit as st
from google import genai

st.set_page_config(page_title="AI Email Generator Assistant", page_icon="✉️")

st.title("✉️ AI Email Generator Assistant")
st.write("Create a professional email/post with a caption and relevant hashtags using Google Gemini.")

# -----------------------------
# API client
# -----------------------------
def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("GEMINI_API_KEY is missing. Add it in Streamlit Cloud → Settings → Secrets.")
        st.stop()
    return genai.Client(api_key=api_key)

# -----------------------------
# User inputs
# -----------------------------
content_type = st.selectbox(
    "Content Type",
    ["Email", "Announcement", "Promotional Post", "Professional Update", "Thank You Message"]
)

platform = st.selectbox(
    "Platform",
    ["Email", "LinkedIn", "Facebook", "Instagram", "General"]
)

topic = st.text_area(
    "Topic",
    placeholder="Example: Launch of our new AI training course",
    height=100
)

professional = st.text_input(
    "Professional / Business / Person",
    placeholder="Example: ABC Training Institute"
)

tone = st.selectbox(
    "Tone",
    ["Professional & Respectful", "Friendly & Professional", "Formal", "Warm & Respectful"]
)

audience = st.text_input(
    "Target Audience (optional)",
    placeholder="Example: students, customers, HR managers"
)

generate = st.button("✨ Generate Content", use_container_width=True)

# -----------------------------
# Generate content
# -----------------------------
if generate:
    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    prompt = f"""
You are an expert professional communication and social media writer.

Create content using these requirements:

Content type: {content_type}
Platform: {platform}
Topic: {topic}
Professional/business/person: {professional or "Not specified"}
Tone: {tone}
Target audience: {audience or "General audience"}

Return ONLY the following sections:

SUBJECT:
A short subject line. If the platform is not Email, make it a suitable title.

EMAIL / MAIN CONTENT:
Write a complete, polished message/post. Keep it clear, useful, professional,
respectful, and natural. Do not invent specific facts, prices, dates, phone numbers,
or claims that were not provided.

CAPTION:
Write a short engaging caption suitable for the selected platform.

HASHTAGS:
Provide 8-12 relevant hashtags. Use # before every hashtag.

Make the content ready to copy and paste.
"""

    try:
        client = get_client()

        # Model update: gemini-1.5-flash is stable and supported
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        result = response.text

        st.success("Content generated successfully!")
        st.text_area("Generated Content", result, height=500)

        st.download_button(
            "⬇️ Download as TXT",
            data=result,
            file_name="ai_generated_content.txt",
            mime="text/plain",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Generation failed: {e}")

st.divider()
st.caption("Powered by Google Gemini API + Streamlit")
