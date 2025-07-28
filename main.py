#!/usr/bin/env python3
"""
Qwen-Agent Chatbot System
Main entry point for the application with multiple interfaces.
"""

import uvicorn
import argparse
import sys
from src.api import app
from src.config import Config
from src.webui import launch_webui
from src.cli import main as cli_main


def main():
    """Main function to run the application."""
    parser = argparse.ArgumentParser(description="Qwen-Agent Chatbot")
    parser.add_argument("--mode", choices=["api", "webui", "cli"], default="api",
                       help="Run mode: api (FastAPI server), webui (Gradio interface), cli (command line)")
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
            debug=Config.DEBUG,
            reload=Config.DEBUG
        )
    
    elif args.mode == "webui":
        print(f"🌐 Starting Gradio Web Interface on port {args.webui_port}")
        launch_webui(share=args.share, server_port=args.webui_port)
    
    elif args.mode == "cli":
        print("💻 Starting Command Line Interface")
        # Pass remaining arguments to CLI
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        cli_main()


if __name__ == "__main__":
    main() 