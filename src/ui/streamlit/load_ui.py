import streamlit as st
import requests
from io import BytesIO
from audio_recorder_streamlit import audio_recorder
from src.ui.streamlit.display_result import show_blog_result
from elevenlabs.client import ElevenLabs
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000/blogs"

LANGUAGES = {
    "English": "english",
    "Hindi": "hindi",
    "French": "french",
    "Spanish": "spanish",
    "German": "german"
}

VOICE_MAPPING = {
    "english": "Rachel",
    "hindi": "Domi",
    "french": "Bella",
    "spanish": "Antoni",
    "german": "Elli"
}

def render_input_ui():
    st.title("🎤📝 AI Blog Generator")
    st.markdown("---")

    # Input Selection
    input_type = st.radio("Input Type", ["Text", "Voice"], horizontal=True, key="input_type")
    language = st.selectbox("Language", options=list(LANGUAGES.keys()), key="language")
    output_format = st.radio("Output Format", ["Text", "Voice"], key="output_format")
    tone = st.selectbox("Writing Tone", ["Professional", "Casual", "Academic"], key="tone")
    length = st.slider("Blog Length (words)", 300, 1000, 500, key="length")

    text_input = ""
    audio_bytes = None

    # Text Input Section
    if input_type == "Text":
        text_input = st.text_area(
            "Enter your blog topic", 
            height=100, 
            value="", 
            key="blog_topic",
            placeholder="Example: 'The future of renewable energy...'"
        )
        if not text_input.strip():
            st.warning("Please enter a valid blog topic")
            return None

    # Voice Input Section
    else:
        st.markdown("""
        🎙️ **Voice Recording Guide**:
        1. Click and hold the mic button below  
        2. Speak clearly for 3-5 seconds  
        3. Release to finish  
        """)
        
        audio_bytes = audio_recorder(
            pause_threshold=4.0,  # Longer pause buffer
            energy_threshold=0.01,  # Higher sensitivity
            sample_rate=48000,  # Better audio quality
            key="voice_recorder",
            recording_color="#FF0000",  # Red when recording
            neutral_color="#6C757D",  # Gray when idle
            icon_name="microphone",
            icon_size="2x",
        )
        
        # Real-time audio validation
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            if len(audio_bytes) < 3072:  # ~3KB minimum (3 seconds)
                st.error("""
                🚫 Recording too short!
                - Speak louder/closer to mic  
                - Hold for 3+ seconds  
                - Reduce background noise  
                """)
                return None

    # Generation Button
    if st.button("Generate Blog", 
                type="primary",
                disabled=(input_type == "Voice" and not audio_bytes)):
        
        with st.spinner("Generating your blog..."):
            try:
                # Text Input Processing
                if input_type == "Text":
                    payload = {
                        "input_type": "text",
                        "output_type": output_format.lower(),
                        "text_input": text_input.strip(),
                        "language": LANGUAGES[language],
                        "tone": tone.lower(),
                        "length": str(length)
                    }
                    response = requests.post(API_URL, data=payload, timeout=60)

                # Voice Input Processing
                else:
                    audio_file = BytesIO(audio_bytes)
                    response = requests.post(
                        API_URL,
                        files={"voice_input": ("voice_input.wav", audio_file, "audio/wav")},
                        data={
                            "input_type": "voice",
                            "output_type": output_format.lower(),
                            "language": LANGUAGES[language],
                            "tone": tone.lower(),
                            "length": str(length),
                            "audio_size": str(len(audio_bytes))
                        },
                        timeout=90  # Longer timeout for voice processing
                    )

                # Handle Response
                if response.status_code == 200:
                    result = response.json()
                    
                    # Voice Output Handling
                    if output_format.lower() == "voice":
                        if 'audio_stream' not in result:
                            st.error("🔇 Voice generation failed - no audio returned")
                            logger.error(f"Backend response missing audio: {result}")
                            return None
                        
                        audio_bytes = result['audio_stream']
                        show_blog_result({
                            "title": result.get("title", ""),
                            "content": result.get("content", ""),
                            "language": result.get("language", "english"),
                            "audio_stream": audio_bytes
                        })
                        
                        # Auto-play and show audio controls
                        st.audio(audio_bytes, format="audio/mp3", start_time=0)
                        
                    # Text Output Handling
                    else:
                        show_blog_result(result)

                else:
                    error_data = response.json()
                    error_msg = error_data.get("error", "Unknown backend error")
                    st.error(f"❌ Generation Failed: {error_msg}")
                    
                    # Helpful tips for common errors
                    if "audio" in error_msg.lower():
                        st.info("💡 Try: 1) Louder speaking 2) Closer to mic 3) Less background noise")
                    logger.error(f"Backend error: {error_data}")

            except requests.exceptions.RequestException as e:
                st.error(f"🌐 Network Error: Failed to connect to server")
                logger.error(f"Request failed: {str(e)}")
            except Exception as e:
                st.error(f"⚡ Unexpected Error: {str(e)}")
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)

    return None