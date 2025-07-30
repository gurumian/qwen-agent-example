#!/usr/bin/env python3
"""
Qwen-Agent with Frontend Integration

This script demonstrates how to run the Qwen-Agent with the frontend
served statically from the same server.
"""

import uvicorn
import os
import sys
from src.api import app
from src.config import Config

def main():
    """Run the application with frontend integration."""
    
    # Check if static directory exists
    static_path = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.exists(static_path):
        print("❌ Static directory not found. Building frontend...")
        build_result = os.system("uv run build_frontend.py")
        if build_result != 0:
            print("❌ Failed to build frontend. Please run 'uv run build_frontend.py'")
            sys.exit(1)
    
    print("✅ Frontend is ready!")
    print(f"🚀 Starting Qwen-Agent with frontend on {Config.HOST}:{Config.PORT}")
    print(f"📱 Frontend will be available at: http://{Config.HOST}:{Config.PORT}")
    print(f"🔧 API documentation: http://{Config.HOST}:{Config.PORT}/docs")
    print(f"📊 API info: http://{Config.HOST}:{Config.PORT}/api/info")
    print(f"⚙️  Frontend config: http://{Config.HOST}:{Config.PORT}/api/config")
    
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        log_level="info",
        reload=False  # Disable reload for production-like experience
    )

if __name__ == "__main__":
    main() 