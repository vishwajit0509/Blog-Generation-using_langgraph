# AI Blog Generation System

A multi-modal AI system that generates blogs from text/voice input with language translation and voice output capabilities.

## 🌟 Features

- **Voice-to-Blog**: Speak your topic, get a formatted blog
- **Multilingual Support**: English, Hindi, French, Spanish, German
- **Customizable Output**: 
  - Control tone (Professional/Casual/Academic)
  - Adjust length (300-1000 words)
- **Voice Synthesis**: ElevenLabs integration for audio output

## 📂 Project Structure

BLOG-GENERATION/
├── blog/                  # Virtual environment
├── src/                   # Core source code
│   ├── llms/              # LLM integrations
│   ├── nodes/             # Workflow nodes
│   ├── states/            # State management
│   └── ui/                # Streamlit interface
├── static/                # Static assets
├── temp_audio/            # Generated voice files
├── .env                   # Environment variables
├── app.py                 # FastAPI backend
├── frontend.py            # Streamlit frontend
├── pyproject.toml         # Project config
├── requirements.txt       # Python dependencies
└── langgraph.json         # Workflow configuration



## 🚀 Quick Start

### Prerequisites

- UV virtual environment manager
- FFmpeg (for audio processing)

### Installation
```bash
# Create virtual environment
uv venv blog

# Activate environment (Windows)
.\blog\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt


# Start backend (FastAPI)
python app.py

![Backend](C:\Users\vishw\OneDrive\Desktop\AGENTIC AI\BLOG-GENERATION\images\backend.png)


# Start frontend (Streamlit)

streamlit run main.py

![Backend](C:\Users\vishw\OneDrive\Desktop\AGENTIC AI\BLOG-GENERATION\images\frontend.png)

