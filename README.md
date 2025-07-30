# Qwen-Agent Chatbot System

A modern chatbot system built on top of the Qwen-Agent framework, providing a FastAPI-based API with support for multiple LLM backends, tools, and streaming responses.

> 📚 **Quick Navigation**: Use `python -m src.doc_cli` for quick access to documentation and source code!

## 📖 Documentation Navigation

### 🚀 Quick Access
```bash
# Open documentation sections
python -m src.doc_cli doc overview
python -m src.doc_cli doc api_reference
python -m src.doc_cli doc extensibility

# Open source files in your editor
python -m src.doc_cli source main_api
python -m src.doc_cli source security

# Open files on GitHub
python -m src.doc_cli github main_api
python -m src.doc_cli github security

# Search documentation and source code
python -m src.doc_cli search "custom tools"
python -m src.doc_cli search "security"

# List all available options
python -m src.doc_cli list all
```

### 🔗 Key Documentation Links
- 📖 **[Project Overview](https://github.com/QwenLM/Qwen-Agent#readme)** - Introduction and features
- 🛠️ **[API Reference](https://github.com/QwenLM/Qwen-Agent/blob/main/README.md#api-usage)** - Complete API documentation
- 🔧 **[Extensibility Guide](docs/EXTENSIBILITY_GUIDE.md)** - Custom tools and security features
- 🚀 **[Quick Start](https://github.com/QwenLM/Qwen-Agent#quick-start)** - Get up and running quickly
- 🔒 **[Security Features](docs/EXTENSIBILITY_GUIDE.md#security-implementation)** - Security implementation details
- 📦 **[Installation Guide](INSTALLATION.md)** - Detailed setup instructions

## Features

- 🤖 **Multi-Model Support**: Compatible with DashScope, OpenAI, and local model servers (vLLM, Ollama)
- 🛠️ **Tool Integration**: Built-in support for code interpreter, web search, image generation, and more
- 📡 **Streaming Responses**: Real-time streaming chat responses
- 🎯 **Task Segmentation**: Pre-configured task types with specialized tools and system messages
- 🖼️ **Multi-Modal Support**: Handle images, documents, URLs, and base64 data seamlessly
- 🔧 **Extensible Architecture**: Easy to add custom tools and agents
- 🌐 **RESTful API**: Clean FastAPI-based API with automatic documentation
- 📁 **File Processing**: Support for document upload and analysis
- 🔒 **Configurable Security**: Environment-based configuration management

## Quick Start

### 0. Prerequisites

Make sure you have Ollama installed and running with the qwen3:14b model:

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull the qwen3:14b model
ollama pull qwen3:14b
```

### 1. Installation

#### Option A: Quick Setup (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd qwen-agent-example

# Run automated setup
./scripts/deploy.sh setup
```

#### Option B: Manual Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd qwen-agent-example

# Install dependencies using uv
uv sync
```

> 📖 **For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md)**

### 2. Configuration

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# For local Ollama (default)
DEFAULT_MODEL=qwen3:14b
DEFAULT_MODEL_TYPE=oai
MODEL_SERVER_URL=http://localhost:11434/v1
MODEL_SERVER_API_KEY=EMPTY

# For DashScope (alternative)
DASHSCOPE_API_KEY=your_dashscope_api_key_here
DEFAULT_MODEL=qwen-max-latest
DEFAULT_MODEL_TYPE=qwen_dashscope
```

### 3. Running the Application

#### **Quick Start**
```bash
# Start development server
./scripts/deploy.sh dev

# Or deploy with Docker
./scripts/deploy.sh docker
```

#### **Manual Options**
```bash
# API Server (Default)
uv run python main.py --mode api

# Web Interface (Gradio)
uv run python main.py --mode webui

# Command Line Interface
uv run python main.py --mode cli

# Using uvicorn directly
uv run uvicorn src.api:app --host 0.0.0.0 --port 8002
```

#### **Web Interface (Gradio)**
```bash
# Launch Gradio web interface
uv run python main.py --mode webui

# With custom port
uv run python main.py --mode webui --webui-port 8080

# With public share link
uv run python main.py --mode webui --share
```

#### **Command Line Interface**
```bash
# Launch interactive CLI
uv run python main.py --mode cli

# Send a single message
uv run python main.py --mode cli --message "Hello, how are you?"

# With specific task
uv run python main.py --mode cli --task "Code Execution"
```

The API will be available at `http://localhost:8002`
The Web Interface will be available at `http://localhost:7860`

### 4. API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8002/docs
- **ReDoc Documentation**: http://localhost:8002/redoc

## API Usage

### Basic Chat

```python
import requests

# Simple chat request
response = requests.post("http://localhost:8002/chat", json={
    "messages": [
        {"role": "user", "content": "Hello! How are you?"}
    ]
})

print(response.json()["content"])
```

### Streaming Chat

```python
import requests

# Streaming chat request
response = requests.post("http://localhost:8002/chat/stream", json={
    "messages": [
        {"role": "user", "content": "Write a Python function to calculate fibonacci numbers"}
    ]
}, stream=True)

for line in response.iter_lines():
    if line:
        data = line.decode('utf-8').replace('data: ', '')
        if data != '[DONE]':
            print(data)
```

### Using Tools

```python
import requests

# Chat with code interpreter tool
response = requests.post("http://localhost:8002/chat", json={
    "messages": [
        {"role": "user", "content": "Calculate 2 + 2 using Python"}
    ],
    "tools": ["code_interpreter"]
})

print(response.json()["content"])
```

### Task-Based Chat

```python
import requests

# Chat with a task-specific agent
response = requests.post("http://localhost:8002/chat/task/code_execution", json={
    "messages": [
        {"role": "user", "content": "Write a Python function to calculate fibonacci numbers"}
    ]
})

print(response.json()["content"])
```

### List Available Tasks

```python
import requests

# Get all available task types
response = requests.get("http://localhost:8002/tasks")
tasks = response.json()

for task in tasks:
    print(f"{task['name']}: {task['description']}")
    print(f"Tools: {task['tools']}")
```

### Multi-Modal Chat

```python
import requests

# Chat with multi-modal input (images, documents, URLs)
response = requests.post("http://localhost:8002/chat", json={
    "messages": [
        {"role": "user", "content": "Analyze this image: https://example.com/image.jpg"}
    ],
    "multimodal": True
})

print(response.json()["content"])
```

### Process Multi-Modal Input

```python
import requests

# Process text with embedded URLs and media
response = requests.post("http://localhost:8002/multimodal/process", json={
    "text": "Check out this image: https://example.com/image.jpg and this document: document.pdf"
})

result = response.json()
print(f"Content: {result['content']}")
print(f"Media items: {result['media']}")
```

### Upload and Process Files

```python
import requests

# Upload a file for processing
with open("document.pdf", "rb") as f:
    files = {"file": ("document.pdf", f, "application/pdf")}
    response = requests.post("http://localhost:8002/multimodal/upload", files=files)

file_info = response.json()
print(f"Uploaded: {file_info}")
```

## Model Configuration

### Local Ollama (Default)

```env
DEFAULT_MODEL=qwen3:14b
DEFAULT_MODEL_TYPE=oai
MODEL_SERVER_URL=http://localhost:11434/v1
MODEL_SERVER_API_KEY=EMPTY
```

### DashScope (Alternative)

```env
DEFAULT_MODEL=qwen-max-latest
DEFAULT_MODEL_TYPE=qwen_dashscope
DASHSCOPE_API_KEY=your_api_key
```

### Local vLLM Server

```env
DEFAULT_MODEL=Qwen2.5-7B-Instruct
DEFAULT_MODEL_TYPE=openai
MODEL_SERVER_URL=http://localhost:8000/v1
MODEL_SERVER_API_KEY=EMPTY
```

## Available Task Types

The system supports various pre-configured task types:

### **General Chat**
- **Description**: General conversation and Q&A
- **Tools**: None (general conversation)
- **Tags**: conversation, qa, general

### **Code Execution**
- **Description**: Execute and analyze code
- **Tools**: code_interpreter
- **Tags**: code, programming, execution

### **Document Analysis**
- **Description**: Analyze and process documents
- **Tools**: file_reader, code_interpreter
- **Tags**: document, analysis, pdf, text

### **Image Generation**
- **Description**: Generate images from text descriptions
- **Tools**: image_gen
- **Tags**: image, generation, art, creative

### **Image Analysis**
- **Description**: Analyze and describe images
- **Tools**: image_analysis
- **Tags**: image, analysis, vision, description

### **Web Search**
- **Description**: Search the web for information
- **Tools**: web_search
- **Tags**: web, search, information, current

### **Math Solving**
- **Description**: Solve mathematical problems
- **Tools**: code_interpreter
- **Tags**: math, mathematics, calculation, problem-solving

### **Text Summarization**
- **Description**: Summarize and condense text
- **Tools**: None (text processing)
- **Tags**: text, summarization, condensation, analysis

### **Translation**
- **Description**: Translate text between languages
- **Tools**: None (language processing)
- **Tags**: translation, language, multilingual, communication

### **Data Analysis**
- **Description**: Analyze and visualize data
- **Tools**: code_interpreter
- **Tags**: data, analysis, visualization, statistics

## Multi-Modal Support

The system supports various input and output modalities:

### **Supported Input Types**
- **Text**: Plain text, markdown, and structured text
- **Images**: JPG, PNG, GIF, BMP, WebP formats
- **Documents**: PDF, TXT, MD, DOCX, DOC formats
- **URLs**: Direct links to images and documents
- **Base64**: Encoded image and document data

### **Processing Capabilities**
- **Image Analysis**: Extract metadata, format, size, and properties
- **Document Text Extraction**: Extract text from PDFs, Word docs, and text files
- **URL Processing**: Fetch and analyze remote media
- **File Upload**: Direct file upload with automatic processing
- **Temporary File Management**: Automatic cleanup of processed files

### **API Interface Specifications**

The chatbot provides a comprehensive REST API with security features and rate limiting.

#### Core Endpoints
- `GET /health` - Health check with rate limit headers
- `POST /chat` - Chat with the AI agent (rate limited)
- `POST /chat/stream` - Stream chat responses (rate limited)
- `GET /tasks` - List available task types
- `GET /api/info` - Get API capabilities and features
- `GET /api/status` - Get API status and statistics

#### Multi-Modal Endpoints
- `POST /multimodal/process` - Process multi-modal input
- `POST /multimodal/extract-text` - Extract text from documents
- `POST /multimodal/analyze-image` - Analyze image metadata
- `POST /multimodal/upload` - Upload files for processing
- `DELETE /multimodal/cleanup` - Clean up temporary files

#### Security Features
- **Rate Limiting**: 60 requests per minute, 1000 per hour
- **Request Size Validation**: Maximum 10MB per request
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- **CORS Support**: Configurable cross-origin resource sharing

#### Rate Limit Headers
All responses include rate limit information:
- `X-RateLimit-Limit-Minute`: Requests allowed per minute
- `X-RateLimit-Limit-Hour`: Requests allowed per hour  
- `X-RateLimit-Remaining-Minute`: Remaining requests this minute
- `X-RateLimit-Remaining-Hour`: Remaining requests this hour

## User Interfaces

The system provides multiple ways to interact with the chatbot:

### **🌐 Web Interface (Gradio)**
- **Modern UI**: Clean, responsive web interface built with Gradio
- **Task Management**: Dropdown to select and switch between task types
- **Multi-Modal Support**: File upload, image processing, document analysis
- **Chat History**: Persistent conversation history with export functionality
- **Analytics**: Built-in analytics dashboard with chat statistics
- **Real-time Interaction**: Live chat with streaming responses
- **Task Information**: Detailed information about each task type
- **System Status**: Real-time system information and health monitoring

### **💻 Command Line Interface (CLI)**
- **Interactive Commands**: Full-featured command-line interface
- **Task Switching**: Switch between different task types
- **Chat History**: View and export conversation history
- **System Status**: Check API connection and system health
- **Batch Processing**: Send single messages or run in interactive mode
- **Task Information**: Get detailed information about available tasks
- **Export Functionality**: Export chat history to files

### **🔌 API Interface**
- **RESTful API**: Full REST API for programmatic access
- **WebSocket Support**: Real-time streaming responses
- **Multi-Modal Endpoints**: Dedicated endpoints for file processing
- **Agent Management**: Create, manage, and switch between agents
- **Task Configuration**: Dynamic task switching and configuration
- **Health Monitoring**: System health and status endpoints

## Available Tools

The system supports various built-in tools:

- **code_interpreter**: Execute Python code
- **web_search**: Search the web for information
- **image_gen**: Generate images from text descriptions
- **file_reader**: Read and analyze uploaded files
- **image_analysis**: Analyze and describe images

## Project Structure

```
qwen-agent-example/
├── src/                   # Source code
│   ├── __init__.py        # Package initialization
│   ├── api.py             # FastAPI application and endpoints
│   ├── api_security.py    # API security and rate limiting
│   ├── agent_manager.py   # Qwen-Agent instance management
│   ├── config.py          # Configuration management
│   ├── models.py          # Pydantic models
│   ├── task_types.py      # Task segmentation and configuration
│   ├── multimodal.py      # Multi-modal processing and support
│   ├── webui.py           # Gradio web interface
│   └── cli.py             # Command line interface
├── tests/                 # Test suite and results
│   ├── README.md          # Test documentation
│   ├── run_all_tests.py   # Comprehensive test runner
│   ├── view_results.py    # Test results viewer
│   ├── scripts/           # Individual test scripts
│   │   ├── test_api.py    # Core API functionality tests
│   │   ├── test_api_security.py # API security and rate limiting tests
│   │   ├── test_multimodal.py # Multi-modal processing tests
│   │   ├── test_webui.py  # Web interface tests
│   │   └── test_tasks.py  # Task management tests
│   ├── results/           # Test results and reports
│   │   └── test_results_*.json # Timestamped test result files
│   ├── unit/              # Unit tests (future use)
│   ├── integration/       # Integration tests (future use)
│   └── e2e/               # End-to-end tests (future use)
├── workspace/             # Workspace and sample data
│   └── samples/           # Sample datasets for testing
│       ├── images/        # Sample images
│       ├── documents/     # Sample documents
│       └── code/          # Sample code files
├── Qwen-Agent/            # Reference implementation
├── main.py                # Application entry point
├── run_tests.py           # Simple test runner
├── pyproject.toml         # Project configuration and dependencies
├── env.example            # Environment variables template
├── INSTALLATION.md        # Comprehensive installation guide
├── Dockerfile             # Docker container configuration
├── docker-compose.yml     # Docker Compose configuration
├── scripts/               # Development and utility scripts
│   ├── deploy.sh          # Automated deployment script
│   └── dev.sh             # Development setup script
└── README.md              # This file
```

## Testing

The project includes a comprehensive test suite with automated test runners and result tracking.

### Running Tests

#### Run All Tests
```bash
# From project root
python run_tests.py

# Or directly
python tests/run_all_tests.py
```

#### Run Individual Test Suites
```bash
# API functionality tests
uv run python tests/scripts/test_api.py

# Multi-modal processing tests
uv run python tests/scripts/test_multimodal.py

# Web interface tests
uv run python tests/scripts/test_webui.py

# Task management tests
uv run python tests/scripts/test_tasks.py
```

#### View Test Results
```bash
# View latest test results
python tests/view_results.py
```

### Test Categories

- **Integration Tests**: API functionality, multi-modal processing
- **End-to-End Tests**: Web interface and user interactions
- **Unit Tests**: Task management and configuration

### Test Results

Test results are automatically saved to `tests/results/` with timestamps and include:
- Pass/fail statistics
- Execution duration
- System information
- Detailed output logs

For more information, see [tests/README.md](tests/README.md).

## Development

### Adding Custom Tools

You can add custom tools by extending the Qwen-Agent framework:

```python
from qwen_agent.tools.base import BaseTool, register_tool

@register_tool('my_custom_tool')
class MyCustomTool(BaseTool):
    description = 'Description of what this tool does'
    parameters = [{
        'name': 'param1',
        'type': 'string',
        'description': 'Parameter description',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        # Your tool implementation
        return "Tool result"
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8002` |
| `DEBUG` | Debug mode | `False` |
| `DEFAULT_MODEL` | Default model name | `qwen-max-latest` |
| `DEFAULT_MODEL_TYPE` | Model type | `qwen_dashscope` |
| `DASHSCOPE_API_KEY` | DashScope API key | None |
| `OPENAI_API_KEY` | OpenAI API key | None |
| `MODEL_SERVER_URL` | Local model server URL | None |
| `MODEL_SERVER_API_KEY` | Local model server API key | `EMPTY` |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Acknowledgments

- Built on top of [Qwen-Agent](https://github.com/QwenLM/Qwen-Agent) framework
- Powered by [Qwen](https://github.com/QwenLM/Qwen) language models
- API framework by [FastAPI](https://fastapi.tiangolo.com/) 

# Frontend Integration Guide

This guide explains how to serve the Qwen-Agent frontend statically with the FastAPI backend, allowing you to determine the API host address programmatically.

## 🚀 Quick Start

### Option 1: Using the New Frontend Mode (Recommended)

```bash
# Build the frontend and copy to static directory
uv run build_frontend.py

# Run with frontend integration
uv run main.py --mode frontend
```

### Option 2: Using the Dedicated Frontend Script

```bash
# Build and run in one command
uv run run_with_frontend.py
```

## 🏗️ Architecture

### Static File Serving
- **Frontend Build**: Webpack builds the frontend into `frontend/dist/`
- **Static Directory**: Built files are copied to `/static/` in the project root
- **FastAPI Serving**: Static files are served from `/static/` path
- **Root Route**: The main HTML is served at `/` with API routes at `/api/*`

### Dynamic API Configuration
- **Frontend Discovery**: Frontend automatically detects the current server host/port
- **Backend Config**: `/api/config` endpoint provides server configuration
- **Programmatic URLs**: API endpoints are determined at runtime

## 📁 Directory Structure

```
qwen-agent-example/
├── frontend/              # Frontend source code
│   ├── src/               # Source files
│   ├── dist/              # Webpack build output
│   ├── package.json       # Frontend dependencies
│   └── webpack.config.js  # Webpack configuration
├── static/                # Static files served by FastAPI
│   ├── index.html         # Main HTML file
│   ├── css/               # Compiled CSS
│   └── js/                # Compiled JavaScript
├── src/                   # Backend source code
│   └── api.py             # FastAPI application
├── build_frontend.py      # Build script
├── main.py                # Main entry point
└── run_with_frontend.py   # Frontend runner
```

## ⚙️ Configuration System

### Backend Configuration Endpoint
The `/api/config` endpoint provides:
```json
{
  "api_url": "http://0.0.0.0:8002",
  "host": "0.0.0.0", 
  "port": 8002,
  "endpoints": {
    "chat": "/chat",
    "chat_stream": "/chat/stream",
    "health": "/health",
    "api_info": "/api/info",
    "tasks": "/tasks",
    "multimodal": "/multimodal/*"
  },
  "features": [
    "Multi-modal chat support",
    "Task-based conversations", 
    "Streaming responses",
    "File upload and processing"
  ]
}
```

### Frontend Dynamic Configuration
The frontend automatically:
1. Detects the current server host and port
2. Fetches configuration from `/api/config`
3. Uses the correct API URLs for all requests

## 🌐 URL Structure

- **Frontend**: `http://localhost:8002/`
- **API Documentation**: `http://localhost:8002/docs`
- **API Info**: `http://localhost:8002/api/info`
- **Configuration**: `http://localhost:8002/api/config`
- **Static Assets**: `http://localhost:8002/static/css/`, `http://localhost:8002/static/js/`

## 🔧 Development Workflow

### 1. Frontend Development
```bash
cd frontend
npm run dev          # Development server with hot reload
npm run build        # Production build
npm run build:static # Build and copy to static directory
```

### 2. Backend Development
```bash
# Run with frontend integration
uv run main.py --mode frontend

# Run API only
uv run main.py --mode api
```

### 3. Full Stack Development
```bash
# Terminal 1: Frontend development
cd frontend && npm run dev

# Terminal 2: Backend with frontend
uv run main.py --mode frontend
```

## 🚀 Production Deployment

### Build Process
```bash
# 1. Build frontend
uv run build_frontend.py

# 2. Run production server
uv run main.py --mode frontend --host 0.0.0.0 --port 8002
```

### Docker Deployment
```dockerfile
# Build frontend
RUN cd frontend && npm install && npm run build
RUN cp -r frontend/dist/* static/

# Run application
CMD ["uv", "run", "main.py", "--mode", "frontend"]
```

## 🎨 Customization

### Frontend Styling
- Edit `frontend/src/css/styles.css`
- Uses CSS Custom Properties for easy theming
- Rebuild with `uv run build_frontend.py`

### API Configuration
- Modify `/api/config` endpoint in `src/api.py`
- Add new endpoints to the configuration
- Frontend will automatically pick up changes

### Build Configuration
- Webpack config: `frontend/webpack.config.js`
- Static file paths: Configured for `/static/` mounting
- Build script: `build_frontend.py`

## 🐛 Debugging

### Frontend Issues
```bash
# Check if static files exist
ls -la static/

# Rebuild frontend
uv run build_frontend.py

# Check webpack build
cd frontend && npm run build
```

### Backend Issues
```bash
# Check API endpoints
curl http://localhost:8002/api/config

# Check static file serving
curl http://localhost:8002/static/css/main.*.css
```

### Common Issues
1. **404 on API endpoints**: Ensure static mounting doesn't override API routes
2. **Missing static files**: Run `uv run build_frontend.py`
3. **CORS issues**: Backend includes CORS middleware for development

## 🔒 Security Considerations

### Production Security
- Static files are served from dedicated `/static/` path
- API routes are protected and separate from static serving
- CORS is configured for development but should be restricted in production

### Development vs Production
- **Development**: CORS allows all origins for easy testing
- **Production**: Configure CORS to allow only specific domains
- **Static Files**: Served with appropriate cache headers

## 📊 Monitoring

### Health Checks
- **API Health**: `GET /health`
- **Frontend Status**: Check browser console for errors
- **Static Files**: Verify `/static/` paths are accessible

### Logging
- FastAPI logs show all requests
- Static file requests are logged
- API errors are properly handled

## 🔧 Troubleshooting

### Build Issues
```bash
# Clean and rebuild
rm -rf frontend/dist static/
uv run build_frontend.py
```

### Server Issues
```bash
# Check if port is in use
lsof -i :8002

# Run with debug logging
uv run main.py --mode frontend --debug
```

### Frontend Not Loading
1. Check browser console for errors
2. Verify static files are accessible
3. Ensure API endpoints are working
4. Check network tab for failed requests

## ✅ Benefits of This Setup

### 1. **Unified Deployment**
- Single server serves both frontend and API
- No need for separate frontend hosting
- Simplified deployment process

### 2. **Dynamic Configuration**
- Frontend automatically adapts to server configuration
- No hardcoded API URLs
- Easy environment switching

### 3. **Development Efficiency**
- Hot reload for frontend development
- Integrated debugging
- Single command to run full stack

### 4. **Production Ready**
- Optimized static file serving
- Proper caching headers
- Security best practices

### 5. **Flexible Architecture**
- Easy to modify and extend
- Clear separation of concerns
- Scalable structure

This setup provides the best of both worlds: the convenience of a unified server with the flexibility of modern frontend development tools. 