# Installation and Deployment Guide

This guide provides comprehensive instructions for installing and deploying the Qwen-Agent Chatbot System.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites](#prerequisites)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [Deployment Options](#deployment-options)
6. [Development Setup](#development-setup)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **Python**: 3.10 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 10GB free space
- **OS**: Linux, macOS, or Windows (WSL recommended for Windows)

### Recommended Requirements
- **Python**: 3.11 or higher
- **RAM**: 16GB or higher
- **Storage**: 20GB free space
- **GPU**: NVIDIA GPU with CUDA support (optional, for local models)

## Prerequisites

### 1. Python Installation

Ensure you have Python 3.10+ installed:

```bash
# Check Python version
python --version

# If Python 3.10+ is not installed, install it:
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip

# macOS (using Homebrew)
brew install python@3.11

# Windows
# Download from https://www.python.org/downloads/
```

### 2. Model Server Setup

#### Option A: Ollama (Recommended for Local Development)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull the qwen3:14b model
ollama pull qwen3:14b

# Verify installation
ollama list
```

#### Option B: DashScope (Cloud-based)

```bash
# No installation required, just API key needed
# Get your API key from: https://dashscope.console.aliyun.com/
```

#### Option C: OpenAI API

```bash
# No installation required, just API key needed
# Get your API key from: https://platform.openai.com/api-keys
```

### 3. Package Manager Setup

#### Option A: uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

#### Option B: pip

```bash
# Ensure pip is up to date
python -m pip install --upgrade pip
```

## Installation Methods

### Method 1: From Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/qwen-agent-example.git
cd qwen-agent-example

# Install dependencies using uv
uv sync

# Or using pip
pip install -e .
```

### Method 2: Using pip (Future Release)

```bash
# Install from PyPI (when published)
pip install qwen-agent-chatbot

# Install with optional dependencies
pip install qwen-agent-chatbot[dev]
```

### Method 3: Using Docker

```dockerfile
# Dockerfile (create this file)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy project files
COPY . .

# Install dependencies
RUN uv sync

# Expose port
EXPOSE 8002

# Run the application
CMD ["uv", "run", "python", "main.py", "--mode", "api"]
```

```bash
# Build and run with Docker
docker build -t qwen-agent-chatbot .
docker run -p 8002:8002 qwen-agent-chatbot
```

## Configuration

### 1. Environment Setup

```bash
# Copy the example environment file
cp env.example .env

# Edit the configuration
nano .env
```

### 2. Environment Variables

```env
# Core Configuration
DEFAULT_MODEL=qwen3:14b
DEFAULT_MODEL_TYPE=oai
MODEL_SERVER_URL=http://localhost:11434/v1
MODEL_SERVER_API_KEY=EMPTY

# Alternative: DashScope Configuration
# DASHSCOPE_API_KEY=your_dashscope_api_key_here
# DEFAULT_MODEL=qwen-max-latest
# DEFAULT_MODEL_TYPE=qwen_dashscope

# Alternative: OpenAI Configuration
# OPENAI_API_KEY=your_openai_api_key_here
# DEFAULT_MODEL=gpt-4
# DEFAULT_MODEL_TYPE=openai

# Server Configuration
HOST=0.0.0.0
PORT=8002
DEBUG=false

# API Security Configuration
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
ALLOWED_ORIGINS=*

# Optional: JWT Configuration (for future auth features)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Model Configuration Examples

#### Local Ollama Setup
```env
DEFAULT_MODEL=qwen3:14b
DEFAULT_MODEL_TYPE=oai
MODEL_SERVER_URL=http://localhost:11434/v1
MODEL_SERVER_API_KEY=EMPTY
```

#### DashScope Setup
```env
DASHSCOPE_API_KEY=your_dashscope_api_key_here
DEFAULT_MODEL=qwen-max-latest
DEFAULT_MODEL_TYPE=qwen_dashscope
```

#### OpenAI Setup
```env
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_MODEL=gpt-4
DEFAULT_MODEL_TYPE=openai
```

## Deployment Options

### 1. Development Deployment

```bash
# Start the API server
uv run python main.py --mode api

# Start the web interface
uv run python main.py --mode webui

# Start the CLI
uv run python main.py --mode cli
```

### 2. Production Deployment

#### Using Gunicorn

```bash
# Install gunicorn
uv add gunicorn

# Create gunicorn configuration
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:8002"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
EOF

# Run with gunicorn
uv run gunicorn src.api:app -c gunicorn.conf.py
```

#### Using Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  qwen-agent-chatbot:
    build: .
    ports:
      - "8002:8002"
    environment:
      - DEFAULT_MODEL=qwen3:14b
      - DEFAULT_MODEL_TYPE=oai
      - MODEL_SERVER_URL=http://ollama:11434/v1
    depends_on:
      - ollama
    volumes:
      - ./workspace:/app/workspace
      - ./temp_uploads:/app/temp_uploads

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:
```

```bash
# Run with Docker Compose
docker-compose up -d
```

#### Using Systemd (Linux)

```bash
# Create systemd service file
sudo tee /etc/systemd/system/qwen-agent-chatbot.service << EOF
[Unit]
Description=Qwen-Agent Chatbot
After=network.target

[Service]
Type=simple
User=qwen-agent
WorkingDirectory=/opt/qwen-agent-chatbot
Environment=PATH=/opt/qwen-agent-chatbot/.venv/bin
ExecStart=/opt/qwen-agent-chatbot/.venv/bin/python main.py --mode api
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl enable qwen-agent-chatbot
sudo systemctl start qwen-agent-chatbot
```

### 3. Cloud Deployment

#### AWS EC2

```bash
# Launch EC2 instance (Ubuntu 22.04 recommended)
# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-pip curl

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup project
git clone https://github.com/your-username/qwen-agent-example.git
cd qwen-agent-example
uv sync

# Configure environment
cp env.example .env
# Edit .env with your configuration

# Run with gunicorn
uv add gunicorn
uv run gunicorn src.api:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8002
```

#### Google Cloud Run

```dockerfile
# Dockerfile for Cloud Run
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY . .
RUN uv sync

EXPOSE 8002

CMD ["uv", "run", "python", "main.py", "--mode", "api"]
```

```bash
# Deploy to Cloud Run
gcloud builds submit --tag gcr.io/YOUR_PROJECT/qwen-agent-chatbot
gcloud run deploy qwen-agent-chatbot \
  --image gcr.io/YOUR_PROJECT/qwen-agent-chatbot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8002
```

## Development Setup

### 1. Development Dependencies

```bash
# Install development dependencies
uv sync --extra dev

# Or manually install dev tools
uv add pytest pytest-asyncio black isort flake8
```

### 2. Code Formatting

```bash
# Format code with black
uv run black src/ tests/

# Sort imports with isort
uv run isort src/ tests/

# Check code style with flake8
uv run flake8 src/ tests/
```

### 3. Testing

```bash
# Run all tests
uv run python run_tests.py

# Run specific test categories
uv run python tests/scripts/test_api.py
uv run python tests/scripts/test_multimodal.py
uv run python tests/scripts/test_webui.py
uv run python tests/scripts/test_tasks.py
uv run python tests/scripts/test_api_security.py

# Run with coverage
uv add pytest-cov
uv run pytest --cov=src tests/
```

### 4. Pre-commit Hooks

```bash
# Install pre-commit
uv add pre-commit

# Setup pre-commit hooks
uv run pre-commit install
```

## Troubleshooting

### Common Issues

#### 1. Python Version Issues
```bash
# Error: Python version not supported
# Solution: Ensure Python 3.10+ is installed
python --version
```

#### 2. Ollama Connection Issues
```bash
# Error: Cannot connect to Ollama
# Solution: Check if Ollama is running
curl http://localhost:11434/v1/models

# Start Ollama if not running
ollama serve
```

#### 3. Port Already in Use
```bash
# Error: Port 8002 already in use
# Solution: Change port or kill existing process
lsof -ti:8002 | xargs kill -9

# Or use different port
uv run python main.py --mode api --port 8003
```

#### 4. Memory Issues
```bash
# Error: Out of memory
# Solution: Reduce model size or increase system memory
# Use smaller model
ollama pull qwen3:1.5b  # Instead of qwen3:14b
```

#### 5. Permission Issues
```bash
# Error: Permission denied
# Solution: Check file permissions
chmod +x scripts/dev.sh
chmod -R 755 workspace/
```

### Getting Help

1. **Check the logs**: Look for error messages in the console output
2. **Verify configuration**: Ensure all environment variables are set correctly
3. **Test connectivity**: Verify model server is accessible
4. **Check dependencies**: Ensure all packages are installed correctly
5. **Review documentation**: Check the README.md for additional information

### Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the README.md and this guide
- **Community**: Join our Discord/Telegram for community support

## Sample Datasets

The system includes sample datasets for testing:

- **Sample Images**: Located in `workspace/samples/images/`
- **Sample Documents**: Located in `workspace/samples/documents/`
- **Sample Code**: Located in `workspace/samples/code/`

To use sample data:

```bash
# Copy sample data to workspace
cp -r workspace/samples/* workspace/

# Test with sample data
curl -X POST http://localhost:8002/multimodal/upload \
  -F "file=@workspace/samples/images/sample.jpg"
```

## Tagging Standards

### Git Tags

```bash
# Create version tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# Create development tag
git tag -a v0.1.0-dev -m "Development version 0.1.0"
git push origin v0.1.0-dev
```

### Docker Tags

```bash
# Tag Docker image
docker tag qwen-agent-chatbot:latest qwen-agent-chatbot:v0.1.0
docker push your-registry/qwen-agent-chatbot:v0.1.0
```

This completes the installation and deployment guide. The system is now ready for production use with comprehensive security features, monitoring, and scalability options. 