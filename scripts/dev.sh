#!/bin/bash

# Development script for Qwen-Agent Chatbot

set -e

echo "🚀 Qwen-Agent Chatbot Development Setup"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "⚠️  Ollama is not running. Please start Ollama first:"
    echo "   ollama serve"
    echo "   ollama pull qwen3:14b"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
fi

# Run the application
echo "🏃 Starting the application..."
uv run python main.py 