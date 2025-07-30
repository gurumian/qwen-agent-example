#!/usr/bin/env python3
"""
Qwen-Agent Chatbot System
Main entry point for the application with multiple interfaces.
"""

import uvicorn
import argparse
import sys
import os
from src.api import app
from src.config import Config
from src.webui import launch_webui
from src.cli import main as cli_main


def main():
    """Main function to run the application."""
    parser = argparse.ArgumentParser(description="Qwen-Agent Chatbot")
    parser.add_argument("--mode", choices=["api", "webui", "cli", "frontend"], default="api",
                       help="Run mode: api (FastAPI server), webui (Gradio interface), cli (command line), frontend (API + static frontend)")
    parser.add_argument("--host", default=Config.HOST, help="Host for API server")
    parser.add_argument("--port", type=int, default=Config.PORT, help="Port for API server")
    parser.add_argument("--webui-port", type=int, default=7860, help="Port for Gradio web interface")
    parser.add_argument("--share", action="store_true", help="Create public share link for web interface")
    
    args = parser.parse_args()
    
    if args.mode == "api":
        print(f"🚀 Starting Qwen-Agent Chatbot API on {args.host}:{args.port}")
        print(f"Debug mode: {Config.DEBUG}")
        print(f"Model: {Config.DEFAULT_MODEL}")
        print(f"Model Server: {Config.MODEL_SERVER_URL}")
        
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="debug" if Config.DEBUG else "info",
            reload=Config.DEBUG
        )
    
    elif args.mode == "frontend":
        # Check if static directory exists
        static_path = os.path.join(os.path.dirname(__file__), "static")
        if not os.path.exists(static_path):
            print("❌ Static directory not found. Building frontend...")
            build_result = os.system("uv run build_frontend.py")
            if build_result != 0:
                print("❌ Failed to build frontend. Please run 'uv run build_frontend.py'")
                sys.exit(1)
        
        print(f"🚀 Starting Qwen-Agent with Frontend on {args.host}:{args.port}")
        print(f"📱 Frontend: http://{args.host}:{args.port}")
        print(f"🔧 API docs: http://{args.host}:{args.port}/docs")
        print(f"📊 API info: http://{args.host}:{args.port}/api/info")
        print(f"⚙️  Config: http://{args.host}:{args.port}/api/config")
        print(f"Debug mode: {Config.DEBUG}")
        print(f"Model: {Config.DEFAULT_MODEL}")
        print(f"Model Server: {Config.MODEL_SERVER_URL}")
        
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="debug" if Config.DEBUG else "info",
            reload=Config.DEBUG
        )
    
    elif args.mode == "webui":
        print(f"🌐 Starting Gradio Web Interface on port {args.webui_port}")
        launch_webui(share=args.share, server_port=args.webui_port)
    
    elif args.mode == "cli":
        print("💻 Starting Command Line Interface")
        # Create a simple test for CLI functionality
        try:
            import requests
            response = requests.post("http://localhost:8002/chat", json={
                "messages": [{"role": "user", "content": "Hello from CLI test"}]
            })
            if response.status_code == 200:
                result = response.json()
                print(f"✅ CLI test successful: {result['content'][:100]}...")
            else:
                print(f"❌ CLI test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ CLI test error: {e}")


if __name__ == "__main__":
    main() 