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

# LangSmith Setup (if used)
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "Blog-Generation")

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
    Now with ElevenLabs streaming for voice output
    """
    try:
        language = language.lower()
        if language not in [lang.value for lang in Language]:
            return JSONResponse(
                {"error": f"Invalid language. Supported: {[lang.value for lang in Language]}"},
                status_code=400
            )

        # Initialize state with all parameters
        state = {
            "language": language,
            "current_language": language,
            "tone": tone.lower(),
            "length": length
        }

        # Handle voice input
        if input_type == "voice":
            if not voice_input:
                return JSONResponse({"error": "Voice file required when input_type=voice"}, status_code=400)

            temp_path = f"temp_{voice_input.filename}"
            with open(temp_path, "wb") as f:
                f.write(await voice_input.read())

            try:
                validate_audio_path(temp_path)
                state["voice_input_path"] = temp_path
                logger.info(f"Voice input saved to {temp_path}")
            except Exception as e:
                logger.error(f"Invalid audio file: {str(e)}")
                return JSONResponse({"error": f"Invalid audio file: {str(e)}"}, status_code=400)

        # Handle text input
        elif input_type == "text":
            if not text_input:
                return JSONResponse({"error": "Text input required when input_type=text"}, status_code=400)
            state["topic"] = text_input.strip()

        # Decide which graph to use
        usecase = "voice" if input_type == "voice" else "language" if language != "english" else "topic"
        logger.info(f"Using graph for usecase: {usecase}")

        # Execute graph
        llm = GroqLLM().get_llm()
        graph = GraphBuilder(llm).setup_graph(usecase)
        result = graph.invoke(state)

        # Clean up temp voice file if exists
        if input_type == "voice" and os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"Removed temporary voice file: {temp_path}")

        # Handle voice output with ElevenLabs streaming
        if output_type == "voice":
            content = result.get("blog", {}).get("content", "")
            if not content:
                logger.error("No content available for voice generation")
                return JSONResponse({"error": "No content to convert to speech"}, status_code=400)

            try:
                # Get appropriate voice for language
                voice = VOICE_MAPPING.get(language, "Rachel")
                logger.info(f"Generating voice output with voice: {voice}")

                # Generate streaming audio
                audio_stream = ELEVENLABS_CLIENT.generate(
                    text=content,
                    voice=voice,
                    model="eleven_monolingual_v2",
                    stream=True
                )
                
                # Convert generator to bytes
                audio_bytes = b"".join([chunk for chunk in audio_stream])
                audio_file = io.BytesIO(audio_bytes)
                
                # Prepare response with metadata in headers
                headers = {
                    "title": result.get("blog", {}).get("title", ""),
                    "content-length": str(len(audio_bytes)),
                    "language": language
                }
                
                return StreamingResponse(
                    audio_file,
                    media_type="audio/mp3",
                    headers=headers
                )

            except Exception as e:
                logger.error(f"Voice generation failed: {str(e)}")
                return JSONResponse(
                    {"error": "Voice generation failed", "details": str(e)},
                    status_code=500
                )

        # Text response
        return JSONResponse({
            "title": result.get("blog", {}).get("title", ""),
            "content": result.get("blog", {}).get("content", ""),
            "language": language
        })

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        return JSONResponse(
            {"error": "Processing failed", "details": str(e)},
            status_code=500
        )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)