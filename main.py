import streamlit as st
from src.ui.streamlit.load_ui import render_input_ui
from src.ui.streamlit.display_result import show_blog_result

def main():
    st.set_page_config(
        page_title="AI Blog Generator",
        page_icon="📝",
        layout="centered"
    )

    st.markdown("# 🌍 Multilingual AI Blog Generator")
    st.markdown(
        "Generate engaging blog content in English, Hindi, or French using AI. "
        "Enter your topic, select a language, and let the AI do the writing!"
    )

    st.markdown("---")

    blog_data = render_input_ui()

    st.markdown("---")

    if blog_data:
        show_blog_result(blog_data)

if __name__ == "__main__":
    main()
