import os
import streamlit as st
from google import genai
from google.genai.errors import APIError

# Page setup
st.set_page_config(page_title="AI Content & Email Generator", page_icon="📝")
st.title("📝 AI Content Generator")
st.write("Generate professional emails, social media posts, captions, and hashtags.")

# Get API key from Streamlit secrets or environment variables
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ API Key not found. Please configure your `GEMINI_API_KEY` in Streamlit Secrets.")
    st.stop()

# Initialize Google Gen AI client
client = genai.Client(api_key=api_key)

# Input UI Controls
col1, col2 = st.columns(2)

with col1:
    content_type = st.selectbox(
        "Select Content Type",
        ["Email", "Social Media Post", "Blog Outline", "Newsletter"]
    )
    platform = st.selectbox(
        "Select Platform / Target Audience",
        ["General Email", "LinkedIn", "Twitter / X", "Instagram", "Facebook"]
    )

with col2:
    tone = st.selectbox(
        "Select Tone",
        ["Professional", "Respectful", "Casual", "Friendly", "Persuasive"]
    )
    include_hashtags = st.checkbox("Include Captions & Hashtags", value=True)

topic = st.text_area(
    "Topic / Core Details",
    placeholder="e.g., Requesting a meeting to discuss the Q3 project update...",
    height=100
)

# Generation Action
if st.button("Generate Content", type="primary"):
    if not topic.strip():
        st.warning("Please enter a topic before generating.")
    else:
        with st.spinner("Generating content..."):
            # Construct Prompt
            prompt = f"""
            You are an expert content creator and copywriter.
            Write a complete {content_type} tailored for {platform}.
            
            Tone: {tone}
            Topic Details: {topic}
            
            Format instructions:
            - Provide a clear subject line (if Email) or strong headline/hook.
            - Write the main body clearly adhering to the selected tone.
            """
            
            if include_hashtags:
                prompt += "\n- Include an engaging caption summary and 3-5 relevant hashtags at the end."

            try:
                # Standard active model: gemini-1.5-flash
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt
                )
                
                st.subheader("Generated Output")
                st.markdown(response.text)
                
            except APIError as e:
                st.error(f"Google Gen AI API Error: {e.message}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
