import streamlit as st
from src.ui.streamlit.load_ui import render_input_ui
from src.ui.streamlit.display_result import show_blog_result

def main():
    st.set_page_config(
        page_title="AI Blog Generator",
        page_icon="📝",
        layout="centered"
    )

    st.title("🌍 Multilingual AI Blog Generator")
    st.markdown(
        """
        Generate engaging blog content using AI in multiple languages like **English**, **Hindi**, **French**, and more!
        Just enter a topic, select the output language, and let AI write and narrate it for you.
        """
    )

    st.markdown("---")

    # 🔽 Render Input Form and trigger generation
    blog_data = render_input_ui()

    st.markdown("---")

    # ✅ Display blog content and audio if available
    if blog_data:
        show_blog_result(blog_data)

if __name__ == "__main__":
    main()
