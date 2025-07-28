# Qwen-Agent Chatbot System

A modern chatbot system built on top of the Qwen-Agent framework, providing a FastAPI-based API with support for multiple LLM backends, tools, and streaming responses.

## Features

- 🤖 **Multi-Model Support**: Compatible with DashScope, OpenAI, and local model servers (vLLM, Ollama)
- 🛠️ **Tool Integration**: Built-in support for code interpreter, web search, image generation, and more
- 📡 **Streaming Responses**: Real-time streaming chat responses
- 🎯 **Task Segmentation**: Pre-configured task types with specialized tools and system messages
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

```bash
# Clone the repository
git clone <your-repo-url>
cd qwen-agent-example

# Install dependencies using uv
uv sync
```

### 2. Configuration

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# For local Ollama (default)
DEFAULT_MODEL=qwen3:14b
DEFAULT_MODEL_TYPE=openai
MODEL_SERVER_URL=http://localhost:11434/v1
MODEL_SERVER_API_KEY=EMPTY

# For DashScope (alternative)
DASHSCOPE_API_KEY=your_dashscope_api_key_here
DEFAULT_MODEL=qwen-max-latest
DEFAULT_MODEL_TYPE=qwen_dashscope
```

### 3. Running the Server

```bash
# Quick start with development script
./scripts/dev.sh

# Or manually
uv run python main.py

# Or using uvicorn directly
uv run uvicorn src.api:app --host 0.0.0.0 --port 8002
```

The API will be available at `http://localhost:8002`

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

## Model Configuration

### Local Ollama (Default)

```env
DEFAULT_MODEL=qwen3:14b
DEFAULT_MODEL_TYPE=openai
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
├── src/
│   ├── __init__.py
│   ├── api.py              # FastAPI application
│   ├── agent_manager.py    # Agent management
│   ├── config.py           # Configuration management
│   ├── models.py           # Pydantic models
│   └── task_types.py       # Task segmentation and configuration
├── Qwen-Agent/             # Reference implementation
├── main.py                 # Application entry point
├── pyproject.toml          # Project configuration and dependencies
├── env.example            # Environment configuration example
└── README.md              # This file
```

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