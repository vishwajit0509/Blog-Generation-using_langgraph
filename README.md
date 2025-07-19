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
│
├── blog/                           # Virtual environment
│
├── images/                         # Project images
│   ├── backend.png
│   └── frontend.png
│
├── src/                           # Core source code
│   ├── graphs/                    # Graph structures
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── graph_builder.py
│   │
│   ├── llms/                      # LLM integrations
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── groqllm.py
│   │
│   ├── nodes/                     # Workflow nodes
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── blog_node.py
│   │
│   ├── states/                    # State management
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── blogstate.py
│   │
│   └── ui/                        # User interface
│       ├── __pycache__/
│       ├── streamlit/
│       └── __init__.py
│
├── static/                        # Static assets
│
├── outputs/                       # Generated outputs
│
├── temp_audio/                    # Generated voice files
│
├── .env                          # Environment variables
├── .env_example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── .python-version               # Python version specification
├── app.py                        # FastAPI backend
├── langgraph.json                # Workflow configuration
├── main.py                       # Streamlit frontend
├── pyproject.toml                # Project configuration
├── requirements.txt              # Python dependencies
├── research.ipynb                # Research notebook
├── test_blog_requests.py         # API testing script
└── uv.lock                       # UV lock file


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

# Start frontend (Streamlit)
streamlit run main.py



