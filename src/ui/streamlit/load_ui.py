# src/ui/streamlit/load_ui.py

import streamlit as st
import requests
from src.ui.streamlit.display_result import show_blog_result  

API_URL = "http://localhost:8000/blogs"

def render_input_ui():
    st.title("📝 AI Blog Generator")

    with st.form(key="blog_form"):
        topic = st.text_input("Enter a blog topic", placeholder="e.g., Benefits of AI in Education")
        language = st.selectbox("Choose Language", ["English", "Hindi", "French", "Spanish", "German"], index=0)
        submit_button = st.form_submit_button(label="Generate Blog")

    if submit_button:
        if topic:
            with st.spinner("⏳ Generating your AI-powered blog..."):
                payload = {
                    "topic": topic,
                    "language": language.lower()
                }
                try:
                    response = requests.post(API_URL, json=payload)
                    if response.status_code == 200:
                        return response.json().get("data")
                        ##show_blog_result(blog_data)
                        ##return blog_data  # ✅ Return data so main.py can use it too
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")
        else:
            st.warning("⚠️ Please enter a topic to generate the blog.")
