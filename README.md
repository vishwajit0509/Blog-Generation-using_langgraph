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

```
BLOG-GENERATION/
├── blog/
├── images/
│   ├── backend.png
│   └── frontend.png
├── src/
│   ├── graphs/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── graph_builder.py
│   ├── llms/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── groqllm.py
│   ├── nodes/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── blog_node.py
│   ├── states/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── blogstate.py
│   └── ui/
│       ├── __pycache__/
│       ├── streamlit/
│       └── __init__.py
├── static/
├── outputs/
├── temp_audio/
├── .env
├── .env_example
├── .gitignore
├── .python-version
├── app.py
├── langgraph.json
├── main.py
├── pyproject.toml
├── requirements.txt
├── research.ipynb
├── test_blog_requests.py
└── uv.lock
```

## 📁 Directory Descriptions

- **blog/** - Virtual environment
- **images/** - Project images (backend.png, frontend.png)
- **src/** - Core source code
  - **graphs/** - Graph structures and workflow management
  - **llms/** - LLM integrations (Groq)
  - **nodes/** - Workflow processing nodes
  - **states/** - Application state management
  - **ui/** - User interface components (Streamlit)
- **static/** - Static assets
- **outputs/** - Generated blog outputs
- **temp_audio/** - Generated voice files

## 🚀 Quick Start

### Prerequisites

- Python 3.x (version specified in `.python-version`)
- UV virtual environment manager
- FFmpeg (for audio processing)

### Installation

```bash
# Create virtual environment
uv venv blog

# Activate environment (Windows)
.\blog\Scripts\activate
# OR (Linux/Mac)
source blog/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### Environment Setup

```bash
# Copy environment template
cp .env_example .env

# Edit .env file with your API keys
# - GROQ API key
# - ElevenLabs API key
# - Other service credentials
```

### Running the Application

```bash
# Start backend (FastAPI)
python app.py

# Start frontend (Streamlit) - in another terminal
streamlit run main.py
```



## 📊 Development

- `research.ipynb` - Jupyter notebook for experimentation and research
- `langgraph.json` - Configuration for workflow management
- `pyproject.toml` - Modern Python project configuration

## 🔧 Architecture

The system uses a modular architecture with:

- **Graphs**: Workflow management and orchestration
- **LLMs**: Language model integrations (Groq)
- **Nodes**: Individual processing components
- **States**: Application state management
- **UI**: User interface components (Streamlit)