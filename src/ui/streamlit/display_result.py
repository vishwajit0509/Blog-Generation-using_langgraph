# src/ui/streamlit/display_result.py
import streamlit as st
import requests
from io import BytesIO

def show_blog_result(result_data):
    """Display blog content and handle both traditional and streaming audio output"""
    if not result_data:
        st.warning("No content to display")
        return
        
    st.markdown("---")
    st.subheader("✨ Generated Blog")
    
    # Blog Content
    with st.container():
        st.markdown(f"### {result_data.get('title', '')}")
        st.markdown(result_data.get('content', ''), unsafe_allow_html=True)
    
    # Handle both traditional and streaming audio output
    if 'voice_url' in result_data or 'audio_stream' in result_data:
        st.markdown("---")
        st.subheader("🔊 Audio Version")
        
        if 'voice_url' in result_data:  # Traditional file-based approach
            st.audio(result_data['voice_url'], format='audio/mp3')
        elif 'audio_stream' in result_data:  # New streaming approach
            audio_bytes = result_data['audio_stream']
            st.audio(audio_bytes, format='audio/mp3')
    
    # Download Options
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download Text",
            data=result_data.get('content', ''),
            file_name="generated_blog.md",
            mime="text/markdown"
        )
    with col2:
        if 'voice_url' in result_data:
            st.download_button(
                label="Download Audio",
                data=requests.get(result_data['voice_url']).content,
                file_name="blog_audio.mp3",
                mime="audio/mp3"
            )
        elif 'audio_stream' in result_data:
            st.download_button(
                label="Download Audio",
                data=result_data['audio_stream'],
                file_name="blog_audio.mp3",
                mime="audio/mp3"
            )
    
    st.success("✅ Blog generation complete!")