from src.states.blogstate import BlogState, Language
from langchain_core.messages import SystemMessage, HumanMessage
import assemblyai as aai
import os
import requests
from pydub import AudioSegment
from typing import Dict, Any
import logging

# Configure audio converter path
AudioSegment.converter = "C:\\ffmpeg\\bin\\ffmpeg.exe"  # replace path if different

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlogNode:
    """Handles blog generation pipeline including text and voice processing."""
    
    def __init__(self, llm):
        self.llm = llm
        aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
        self.assemblyai_client = aai
        self.supported_languages = [lang.value for lang in Language]

    def voice_input_node(self, state: BlogState) -> Dict[str, Any]:
        """Transcribe voice file to text using AssemblyAI."""
        voice_path = state.get("voice_input_path")
        if not voice_path:
            raise ValueError("Missing voice_input_path in state")

        try:
            logger.info(f"Starting transcription for {voice_path}")
            transcriber = self.assemblyai_client.Transcriber()
            transcript = transcriber.transcribe(voice_path)
            logger.info(f"Transcription complete: {len(transcript.text)} characters")
            
            return {
                "topic": transcript.text,
                "voice_transcript": transcript.text,
                "language": state.get("language", "english")  # Preserve language
            }
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    def title_creation(self, state: BlogState) -> Dict[str, Any]:
        """Generate blog title based on topic."""
        topic = state.get("topic", "")
        language = state.get("language", "english")
        
        if not topic:
            return {}
            
        prompt = f"""
        You are an expert blog content writer. Use markdown formatting.
        Generate a creative, engaging blog title in {language} for the topic: '{topic}'
        Return ONLY the title text without any additional commentary.
        """
        
        response = self.llm.invoke(prompt)
        return {"blog": {"title": response.content.strip()}}

    def content_generation(self, state: BlogState) -> Dict[str, Any]:
        """Generate full blog content."""
        topic = state.get("topic", "")
        language = state.get("language", "english")
        
        if not topic or "blog" not in state or "title" not in state["blog"]:
            return {}
            
        prompt = f"""
        You are an expert blog writer. Write in {language} using Markdown formatting.
        Topic: {topic}
        Title: {state['blog']['title']}
        
        Requirements:
        - 500-800 words
        - Use headings (##) and subheadings (###)
        - Include bullet points and numbered lists where appropriate
        - Maintain professional but accessible tone
        """
        
        response = self.llm.invoke(prompt)
        return {
            "blog": {
                "title": state['blog']['title'],
                "content": response.content
            }
        }

    def translation(self, state: BlogState) -> Dict[str, Any]:
        """Translate blog content to target language."""
        target_lang = state.get("current_language", "english")
        content = state.get("blog", {}).get("content", "")
        
        if not content:
            return {}
            
        translation_prompt = f"""
        Translate this blog post to {target_lang} while:
        - Preserving markdown formatting
        - Maintaining technical accuracy
        - Keeping headings and structure
        - Adapting cultural references appropriately
        
        Content to translate:
        {content}
        """
        
        messages = [
            SystemMessage(content=f"You are a professional {target_lang} translator."),
            HumanMessage(content=translation_prompt)
        ]
        
        try:
            translation_result = self.llm.invoke(messages)
            return {
                "blog": {
                    "title": state['blog']['title'],
                    "content": translation_result.content
                }
            }
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise

    def voice_output_node(self, state: BlogState) -> Dict[str, Any]:
        """Convert blog content to speech using Cartesia API."""
        content = state.get("blog", {}).get("content", "")
        if not content:
            return {}
            
        try:
            api_key = os.getenv("CARTESIA_API_KEY")
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "text": content,
                "voice": "nova",
                "output_format": "mp3"
            }
            
            response = requests.post(
                "https://api.cartesia.ai/v1/speech",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            return {
                "voice_output": response.json().get("audio_url"),
                "current_language": state.get("current_language")
            }
        except Exception as e:
            logger.error(f"Voice generation failed: {e}")
            return {}

    def route(self, state: BlogState) -> Dict[str, Any]:
        """Pass-through node for logging."""
        logger.info(f"Routing state with language: {state.get('language')}")
        return state

    def route_decision(self, state: BlogState) -> str:
        """Determine which translation branch to take."""
        lang = state.get("language", "english").lower()
        logger.info(f"Routing decision for language: {lang}")
        return lang if lang in self.supported_languages else "english"