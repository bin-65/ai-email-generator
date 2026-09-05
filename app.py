import os
import streamlit as st
from google import genai
from google.genai.errors import APIError

# Page Configuration
st.set_page_config(page_title="AI Email Generator Assistant", page_icon="✉️")
st.title("✉️ AI Email Generator Assistant")
st.write("Generate customized professional emails with captions and hashtags.")

# Retrieve API key
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ API Key not found. Please add `GEMINI_API_KEY` to Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# Input Controls
col1, col2 = st.columns(2)

with col1:
    platform = st.selectbox(
        "Target Platform / Audience",
        ["General Email", "LinkedIn InMail", "Workplace Slack/Teams Mail", "Cold Outreach Email"]
    )
    tone = st.selectbox(
        "Email Tone",
        ["Professional & Respectful", "Formal", "Friendly & Professional", "Persuasive"]
    )

with col2:
    include_caption = st.checkbox("Include Short Caption & Hashtags", value=True)

topic = st.text_area(
    "Email Topic & Core Details",
    placeholder="e.g., Requesting a meeting to discuss the Q3 project update...",
    height=120
)

# Generation Trigger
if st.button("Generate Email", type="primary"):
    if not topic.strip():
        st.warning("Please enter the email topic or details first.")
    else:
        with st.spinner("Writing your email..."):
            prompt = f"""
            You are a professional email assistant. 
            Write a clear and complete email for {platform}.

            Tone: {tone}
            Topic/Details: {topic}

            Format Requirement:
            - **Subject Line**: Concise and compelling.
            - **Email Body**: Clear greeting, structured paragraphs, professional sign-off.
            """

            if include_caption:
                prompt += "\n- **Caption**: A 1-sentence summary.\n- **Hashtags**: 3-5 relevant hashtags."

            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt
                )
                
                st.subheader("Generated Email Output")
                st.markdown(response.text)
                
            except APIError as e:
                st.error(f"Google Gen AI API Error: {e.message}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
