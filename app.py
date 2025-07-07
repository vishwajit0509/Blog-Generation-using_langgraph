import os
import shutil
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
from elevenlabs.client import ElevenLabs
import io
import logging
from starlette.background import BackgroundTask
import io
from src.llms.groqllm import GroqLLM
from src.graphs.graph_builder import GraphBuilder
from src.states.blogstate import Language, validate_audio_path

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ElevenLabs client
ELEVENLABS_CLIENT = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Voice mapping for different languages
VOICE_MAPPING = {
    "english": "Rachel",
    "hindi": "Domi",
    "french": "Bella",
    "spanish": "Antoni",
    "german": "Elli"
}

# App initialization
app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

def cleanup_temp_file(path: str):
    """Helper function to clean up temporary files"""
    if path and os.path.exists(path):
        try:
            os.remove(path)
            logger.info(f"Removed temporary file: {path}")
        except Exception as e:
            logger.error(f"Failed to remove temporary file {path}: {str(e)}")

@app.post("/blogs")
async def create_blogs(
    request: Request,
    input_type: str = Form("text"),
    output_type: str = Form("text"),
    text_input: Optional[str] = Form(None),
    voice_input: Optional[UploadFile] = None,
    language: str = Form("english"),
    tone: str = Form("professional"),
    length: int = Form(500)
):
    """
    Handles both text and voice input with text/voice output options
    with improved ElevenLabs streaming implementation
    """
    temp_path = None
    try:
        language = language.lower()
        if language not in [lang.value for lang in Language]:
            return JSONResponse(
                {"error": f"Invalid language. Supported: {[lang.value for lang in Language]}"},
                status_code=400
            )

        # Initialize state
        state = {
            "language": language,
            "current_language": language,
            "tone": tone.lower(),
            "length": length
        }

        # Handle input
        if input_type == "voice":
            if not voice_input:
                return JSONResponse({"error": "Voice file required when input_type=voice"}, status_code=400)
            
            temp_path = f"temp_{voice_input.filename}"
            with open(temp_path, "wb") as f:
                shutil.copyfileobj(voice_input.file, f)
            
            try:
                validate_audio_path(temp_path)
                state["voice_input_path"] = temp_path
            except Exception as e:
                logger.error(f"Invalid audio file: {str(e)}")
                return JSONResponse({"error": f"Invalid audio file: {str(e)}"}, status_code=400)
        elif input_type == "text":
            if not text_input:
                return JSONResponse({"error": "Text input required when input_type=text"}, status_code=400)
            state["topic"] = text_input.strip()

        # Process request
        usecase = "voice" if input_type == "voice" else "language" if language != "english" else "topic"
        llm = GroqLLM().get_llm()
        graph = GraphBuilder(llm).setup_graph(usecase)
        result = graph.invoke(state)

        
        # Voice output with proper streaming
        if output_type == "voice":
            content = result.get("blog", {}).get("content", "")
            if not content:
                return JSONResponse({"error": "No content to convert to speech"}, status_code=400)

            voice_id = {
        "english": "EXAVITQu4vr4xnSDxMaL",  # Rachel
        "hindi": "AZnzlk1XvdvUeBnXmlld",    # Domi
        "french": "XB0fDUnXU5powFXDhCwa",    # Bella
        "spanish": "ErXwobaYiN019PkySvjV",   # Antoni
        "german": "MF3mGyEYCl7XYWbV9V6O"     # Elli
    }.get(language, "EXAVITQu4vr4xnSDxMaL")  # Default to Rachel

            logger.info(f"Generating voice output with voice ID: {voice_id}")

    # Create streaming response
            def generate_audio():
                try:
                    audio_generator = ELEVENLABS_CLIENT.text_to_speech.convert(
                text=content,
                voice_id=voice_id,
                model_id="eleven_monolingual_v1",
                output_format="mp3_44100_128"
            )
            
            # Stream the audio chunks directly
                    for chunk in audio_generator:
                        yield chunk
                
                except Exception as e:
                    logger.error(f"Streaming error: {str(e)}")
                    raise

    # Cleanup task
            cleanup = BackgroundTask(cleanup_temp_file, temp_path) if temp_path else None

            return StreamingResponse(
        generate_audio(),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": 'attachment; filename="blog_audio.mp3"',
            "X-Title": result.get("blog", {}).get("title", ""),
            "X-Language": language
        },
        background=cleanup
    )

        # Text output
        if temp_path:
            cleanup_temp_file(temp_path)
        return JSONResponse({
            "title": result.get("blog", {}).get("title", ""),
            "content": result.get("blog", {}).get("content", ""),
            "language": language
        })

    except Exception as e:
        if temp_path:
            cleanup_temp_file(temp_path)
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        return JSONResponse(
            {"error": "Processing failed", "details": str(e)},
            status_code=500
        )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True,timeout_keep_alive=300,timeout_graceful_shutdown=30)