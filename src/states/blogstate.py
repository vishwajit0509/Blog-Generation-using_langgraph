from typing import TypedDict, Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from enum import Enum
import os
from pydub import AudioSegment
from pathlib import Path

# Configure audio converter path
AudioSegment.converter = "C:\\ffmpeg\\bin\\ffmpeg.exe"  # replace path if different

class Language(str, Enum):
    """Supported languages for blog generation and translation"""
    ENGLISH = "english"
    HINDI = "hindi"
    FRENCH = "french"
    SPANISH = "spanish"
    GERMAN = "german"

class BlogContent(BaseModel):
    """Structured blog content with validation"""
    title: str = Field(..., min_length=5, max_length=120, 
                      description="SEO-friendly blog title")
    content: str = Field(..., min_length=300, 
                        description="Markdown formatted blog content")
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        if len(v.split()) < 50:  # Rough word count check
            raise ValueError("Content too short (minimum 50 words)")
        return v

class BlogState(TypedDict, total=False):
    """
    State container for blog generation workflow with type-safe fields.
    All fields are optional to support incremental updates between nodes.
    """
    # Core fields
    topic: Optional[str]
    blog: Optional[BlogContent]
    language: Optional[Language]
    current_language: Optional[Language]
    
    # Voice processing pipeline
    voice_input_path: Optional[Path]  # Path to input audio file
    voice_transcript: Optional[str]   # Raw transcription text
    voice_output_url: Optional[str]   # URL to generated audio
    
    # System fields
    error: Optional[str]             # Error message if processing fails
    warnings: Optional[List[str]]    # Non-critical warnings

    # Metadata
    processing_time: Optional[float] # Time taken in seconds
    source: Optional[str]            # Source of the content

# Type aliases for clearer signatures
BlogStateUpdate = Dict[str, Any]
AudioFormat = str  # e.g., 'mp3', 'wav'

# Utility functions
def validate_audio_path(path: Optional[str]) -> Optional[Path]:
    """Validate and convert audio file path"""
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")
    if p.suffix.lower() not in ['.mp3', '.wav', '.ogg']:
        raise ValueError("Unsupported audio format")
    return p

def create_initial_state(
    topic: str = "",
    language: str = "english",
    voice_path: Optional[str] = None
) -> BlogState:
    """Initialize a validated blog state"""
    return {
        "topic": topic.strip(),
        "language": Language(language.lower()),
        "current_language": Language(language.lower()),
        "voice_input_path": validate_audio_path(voice_path),
        "warnings": []
    }