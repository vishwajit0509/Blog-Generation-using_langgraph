import streamlit as st

def show_blog_result(blog_data):
    if not blog_data:
        st.info("No blog content to display.")
        return

    blog = blog_data.get("blog", {})
    title = blog.get("title", "Untitled")
    content = blog.get("content", "No content generated.")
    audio_url = blog_data.get("voice_output")

    st.markdown("---")
    st.subheader("📌 Blog Title")
    st.markdown(f"#### {title}", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📄 Blog Content")
    st.markdown(content, unsafe_allow_html=True)

    if audio_url:
        st.markdown("---")
        st.subheader("🔊 AI Voice Narration")
        st.audio(audio_url)

    st.markdown("---")
    st.success("✅ Blog generated successfully!")
