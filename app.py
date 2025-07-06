import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.llms.groqllm import GroqLLM
from src.graphs.graph_builder import GraphBuilder
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LangSmith Configuration
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "Blog-Generation")

# Valid languages for input validation
VALID_LANGUAGES = ["english", "hindi", "french", "spanish", "german"]

@app.post("/blogs")
async def create_blogs(request: Request):
    """
    Accepts a JSON payload:
    {
        "topic": "...",                # optional (used in 'topic' and 'language' modes)
        "language": "english",         # optional (required for language & voice)
        "usecase": "topic" | "language" | "voice",   # required
        "audio_path": "path/to/file.mp3"  # optional (used in 'voice')
    }
    """
    data = await request.json()
    topic = data.get("topic", "")
    language = data.get("language", "english").lower()
    usecase = data.get("usecase", "topic").lower()
    audio_path = data.get("audio_path")

    # Input validation
    if language not in VALID_LANGUAGES:
        return {"error": f"Invalid language. Must be one of: {VALID_LANGUAGES}"}
    
    if usecase not in ["topic", "language", "voice"]:
        return {"error": "Invalid usecase. Must be 'topic', 'language', or 'voice'"}

    llm = GroqLLM().get_llm()
    graph_builder = GraphBuilder(llm)
    graph = graph_builder.setup_graph(usecase=usecase)

    # Initial state with proper language fields
    state = {
        "topic": topic,
        "language": language,
        "current_language": language
    }

    # Usecase-specific adjustments
    if usecase == "voice":
        if not audio_path:
            return {"error": "audio_path required for voice usecase"}
        state["voice_input_path"] = audio_path  # Matching BlogNode expectation
        
    elif usecase == "language":
        if not topic:
            return {"error": "topic is required for language usecase"}
        
    elif usecase == "topic":
        if not topic:
            return {"error": "topic is required for topic usecase"}
        # For topic-only mode, we don't need translation
        state["language"] = "english"
        state["current_language"] = "english"

    print(f"Initial state: {state}")  # Debug logging

    # Invoke the graph
    try:
        result = graph.invoke(state)
        print(f"Final result: {result}")  # Debug logging
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "details": "Graph processing failed"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)