# src/ui/streamlit/display_result.py

import streamlit as st

def show_blog_result(blog_data):
    if not blog_data:
        st.info("No blog content to display.")
        return

    blog = blog_data.get("blog", {})
    title = blog.get("title", "Untitled")
    content = blog.get("content", "No content generated.")

    st.markdown("---")
    st.subheader("📌 Blog Title")
    st.markdown(f"#### {title}", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📄 Blog Content")
    st.markdown(content, unsafe_allow_html=True)

    st.markdown("---")
    st.success("✅ Blog generated successfully!")
