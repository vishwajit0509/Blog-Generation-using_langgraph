import streamlit as st
import requests
from io import BytesIO
from audio_recorder_streamlit import audio_recorder
from src.ui.streamlit.display_result import show_blog_result
from elevenlabs.client import ElevenLabs
import base64

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

    input_type = st.radio("Input Type", ["Text", "Voice"], horizontal=True)
    language = st.selectbox("Language", options=list(LANGUAGES.keys()))
    output_format = st.radio("Output Format", ["Text", "Voice"])
    tone = st.selectbox("Writing Tone", ["Professional", "Casual", "Academic"])
    length = st.slider("Blog Length", 300, 1000, 500)

    text_input = ""
    audio_bytes = None

    if input_type == "Text":
        text_input = st.text_area("Enter your blog topic", 
                                height=100, 
                                value="", 
                                key="blog_topic",
                                placeholder="Type your blog topic here...")
        if not text_input.strip():
            st.warning("Please enter a valid blog topic")
            return None
    else:
        # Enhanced microphone recording with immediate feedback
        st.markdown("""
        🎙️ **Voice Recording Instructions:**
        1. Click and hold the mic button
        2. Speak clearly for 2-3 seconds
        3. Release to finish recording
        """)
        
        audio_bytes = audio_recorder(
            pause_threshold=3.0,  # Require 3 seconds of silence to stop
            energy_threshold=0.01,  # More sensitive to quiet speech
            sample_rate=44100,
            key="voice_recorder"
        )
        
        # Immediate audio playback and validation
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            if len(audio_bytes) < 2048:  # Check for minimum audio size (2KB)
                st.error("""
                ❌ Recording too short!
                - Please speak for at least 3 seconds
                - Move closer to microphone
                - Reduce background noise
                """)
                return None

    if st.button("Generate Blog", 
                disabled=(input_type == "Voice" and not audio_bytes)):
        if input_type == "Text" and not text_input.strip():
            st.warning("Please enter a topic.")
            return None

        with st.spinner("Generating your blog..."):
            try:
                if input_type == "Text":
                    response = requests.post(
                        API_URL,
                        data={
                            "input_type": "text",
                            "output_type": output_format.lower(),
                            "text_input": text_input,
                            "language": LANGUAGES[language],
                            "tone": tone.lower(),
                            "length": str(length)
                        }
                    )
                else:
                    # Enhanced voice request with size verification
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
                            "audio_size": str(len(audio_bytes))  # Send size for backend validation
                        },
                        timeout=30  # Increased timeout for voice processing
                    )

                if response.status_code == 200:
                    result = response.json()
                    if output_format.lower() == "voice":
                        if 'audio_stream' not in result:
                            st.error("Voice generation failed - no audio returned")
                            return None
                            
                        audio_bytes = result['audio_stream']
                        show_blog_result({
                            "title": result.get("title", ""),
                            "content": result.get("content", ""),
                            "language": result.get("language", "english"),
                            "audio_stream": audio_bytes
                        })
                        st.audio(audio_bytes, format="audio/mp3")
                    else:
                        show_blog_result(result)
                else:
                    error_msg = response.json().get("error", "Unknown error occurred")
                    st.error(f"❌ Generation Error: {error_msg}")
                    if "audio" in error_msg.lower():
                        st.info("💡 Try speaking louder or reducing background noise")

            except requests.exceptions.RequestException as e:
                st.error(f"🚨 Connection Error: {str(e)}")
            except Exception as e:
                st.error(f"🚨 Unexpected Error: {str(e)}")

    return None