import streamlit as st
from src.ui.streamlit.load_ui import render_input_ui
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Page Configuration
    st.set_page_config(
        page_title="AI Blog Generator",
        page_icon="✍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar with enhanced settings
    with st.sidebar:
        st.title("⚙️ Settings")
        st.markdown("---")
        
        # Check for ElevenLabs API key
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            api_key = st.text_input("ElevenLabs API Key", type="password")
            if api_key:
                st.session_state.elevenlabs_key = api_key
        else:
            st.session_state.elevenlabs_key = api_key
            st.success("✅ ElevenLabs API key loaded from .env")
        
        st.info("""
        **📝 How to use:**
        1. Select input type (Text/Voice)
        2. Choose language and tone
        3. Set desired length
        4. Click Generate
        
        **🎧 Voice Note:**  
        Voice output requires ElevenLabs API key
        """)
        
        st.markdown("---")
        st.caption("Made with ❤️ using Streamlit")

    # Main Content Area
    st.title("🤖 AI-Powered Blog Generator")
    st.markdown("Generate professional blogs in multiple languages with AI")
    st.markdown("---")
    
    # Error boundary
    try:
        # Render UI and handle results
        render_input_ui()
        
    except Exception as e:
        st.error(f"⚠️ An error occurred: {str(e)}")
        st.button("Retry")


if __name__ == "__main__":
    main()