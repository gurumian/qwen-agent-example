#!/usr/bin/env python3
"""
Qwen-Agent Chatbot System
Main entry point for the FastAPI application.
"""

import uvicorn
from src.api import app
from src.config import Config


def main():
    """Main function to run the FastAPI application."""
    print(f"Starting Qwen-Agent Chatbot API on {Config.HOST}:{Config.PORT}")
    print(f"Debug mode: {Config.DEBUG}")
    print(f"Model: {Config.DEFAULT_MODEL}")
    print(f"Model Server: {Config.MODEL_SERVER_URL}")
    
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        reload=Config.DEBUG
    )


if __name__ == "__main__":
    main() 