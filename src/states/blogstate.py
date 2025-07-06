from typing import TypedDict, Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import os
from pydub import AudioSegment
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure audio converter path
AudioSegment.converter = "C:\\ffmpeg\\bin\\ffmpeg.exe"  # replace path if different

class Language(str, Enum):
    """Supported languages for blog generation and translation"""
    ENGLISH = "english"
    HINDI = "hindi"
    FRENCH = "french"
    SPANISH = "spanish"
    GERMAN = "german"
    ITALIAN = "italian"  # New language option

class VoicePreference(str, Enum):
    """Supported voice preferences for TTS"""
    RACHEL = "Rachel"
    DOMI = "Domi"
    BELLA = "Bella"
    ANTONI = "Antoni"
    ELLI = "Elli"
    NOVA = "Nova"  # Additional voice option

class BlogContent(BaseModel):
    """Enhanced structured blog content with validation"""
    title: str = Field(..., min_length=5, max_length=120,
                      description="SEO-friendly blog title")
    content: str = Field(..., min_length=300,
                        description="Markdown formatted blog content")
    tone: str = Field("professional", description="Writing tone/style")
    length: int = Field(500, ge=300, le=2000, description="Word count target")
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        if len(v) > 120:
            logger.warning(f"Title truncated from {len(v)} to 120 characters")
            return v[:117] + "..."
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        word_count = len(v.split())
        if word_count < 50:
            raise ValueError("Content too short (minimum 50 words)")
        if word_count > 2000:
            logger.warning(f"Content exceeds 2000 words ({word_count})")
        return v

class BlogState(TypedDict, total=False):
    """
    Enhanced state container for blog generation workflow with type-safe fields.
    Now supports both file-based and streaming audio output.
    """
    # Core fields
    topic: Optional[str]
    blog: Optional[BlogContent]
    language: Optional[Language]
    current_language: Optional[Language]
    voice_preference: Optional[VoicePreference]  # New field
    
    # Voice processing pipeline
    voice_input_path: Optional[Path]        # Path to input audio file
    voice_transcript: Optional[str]         # Raw transcription text
    voice_output_url: Optional[str]         # URL to generated audio file
    voice_output_stream: Optional[bytes]    # Streaming audio bytes
    
    # System fields
    error: Optional[str]                   # Error message
    warnings: Optional[List[str]]          # Non-critical warnings
    processing_steps: Optional[List[str]]  # Track workflow progress
    
    # Metadata
    processing_time: Optional[float]       # Time taken in seconds
    source: Optional[str]                  # Source of the content
    api_used: Optional[str]                # Which TTS API was used

# Type aliases
BlogStateUpdate = Dict[str, Any]
AudioFormat = str  # e.g., 'mp3', 'wav'

def validate_audio_path(path: Optional[Union[str, Path]]) -> Optional[Path]:
    """Enhanced audio file validation with better error handling"""
    if not path:
        return None
    
    try:
        p = Path(path) if not isinstance(path, Path) else path
        if not p.exists():
            raise FileNotFoundError(f"Audio file not found: {p}")
        
        # Verify file is actually audio
        try:
            AudioSegment.from_file(p).duration_seconds > 0
        except Exception as e:
            raise ValueError(f"Invalid audio file: {str(e)}")
        
        if p.suffix.lower() not in ['.mp3', '.wav', '.ogg', '.flac']:
            logger.warning(f"Potentially unsupported audio format: {p.suffix}")
            
        return p
    except Exception as e:
        logger.error(f"Audio validation failed: {str(e)}")
        raise

def create_initial_state(
    topic: str = "",
    language: str = "english",
    voice_path: Optional[Union[str, Path]] = None,
    tone: str = "professional",
    length: int = 500,
    voice_preference: Optional[str] = None
) -> BlogState:
    """Enhanced state initialization with new parameters"""
    try:
        lang = Language(language.lower())
        voice_pref = VoicePreference(voice_preference) if voice_preference else None
        
        return {
            "topic": topic.strip(),
            "language": lang,
            "current_language": lang,
            "voice_input_path": validate_audio_path(voice_path),
            "voice_preference": voice_pref,
            "tone": tone.lower(),
            "length": length,
            "warnings": [],
            "processing_steps": ["initialized"],
            "api_used": "elevenlabs"  # Default to ElevenLabs
        }
    except Exception as e:
        logger.error(f"State initialization failed: {str(e)}")
        raise