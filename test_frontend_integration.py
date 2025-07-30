#!/usr/bin/env uv run
"""
Test script for frontend integration

This script tests the key components of the frontend integration:
1. Static file serving
2. API endpoints
3. Frontend configuration
4. Chat functionality
"""

import requests
import time
import sys
import os

def test_api_endpoints(base_url):
    """Test all API endpoints."""
    print(f"🔍 Testing API endpoints at {base_url}")
    
    # Test /api/config
    try:
        response = requests.get(f"{base_url}/api/config")
        if response.status_code == 200:
            config = response.json()
            print(f"✅ /api/config: {config['api_url']}")
        else:
            print(f"❌ /api/config: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ /api/config error: {e}")
        return False
    
    # Test /health
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print(f"✅ /health: OK")
        else:
            print(f"❌ /health: {response.status_code}")
    except Exception as e:
        print(f"❌ /health error: {e}")
    
    # Test /api/info
    try:
        response = requests.get(f"{base_url}/api/info")
        if response.status_code == 200:
            info = response.json()
            print(f"✅ /api/info: {info['name']} v{info['version']}")
        else:
            print(f"❌ /api/info: {response.status_code}")
    except Exception as e:
        print(f"❌ /api/info error: {e}")
    
    return True

def test_static_files(base_url):
    """Test static file serving."""
    print(f"📁 Testing static files at {base_url}")
    
    # Test main HTML
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200 and "Qwen Agent" in response.text:
            print(f"✅ / (HTML): OK")
        else:
            print(f"❌ / (HTML): {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ / (HTML) error: {e}")
        return False
    
    # Test static CSS
    try:
        response = requests.get(f"{base_url}/static/css/main.942af4bf1334cf08d235.css")
        if response.status_code == 200:
            print(f"✅ /static/css: OK")
        else:
            print(f"❌ /static/css: {response.status_code}")
    except Exception as e:
        print(f"❌ /static/css error: {e}")
    
    # Test static JS
    try:
        response = requests.get(f"{base_url}/static/js/main.392d2a9a41ab9436b1b6.js")
        if response.status_code == 200:
            print(f"✅ /static/js: OK")
        else:
            print(f"❌ /static/js: {response.status_code}")
    except Exception as e:
        print(f"❌ /static/js error: {e}")
    
    return True

def test_chat_functionality(base_url):
    """Test chat functionality."""
    print(f"💬 Testing chat functionality at {base_url}")
    
    # Test chat stream endpoint
    try:
        messages = '[{"role":"user","content":"Hi"}]'
        params = {
            'messages': messages,
            'task_name': 'General Chat',
            'stream': 'true'
        }
        response = requests.get(f"{base_url}/chat/stream", params=params, stream=True)
        if response.status_code == 200:
            print(f"✅ /chat/stream: OK")
            # Read a few lines to verify streaming
            lines = []
            for line in response.iter_lines():
                if line:
                    lines.append(line.decode('utf-8'))
                    if len(lines) >= 3:
                        break
            if lines:
                print(f"   📡 Streaming: {len(lines)} lines received")
        else:
            print(f"❌ /chat/stream: {response.status_code}")
    except Exception as e:
        print(f"❌ /chat/stream error: {e}")

def main():
    """Main test function."""
    print("🧪 Frontend Integration Test")
    print("=" * 50)
    
    # Default to localhost:8002
    base_url = "http://localhost:8002"
    
    # Check if static directory exists
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.exists(static_dir):
        print("❌ Static directory not found!")
        print("   Run 'uv run build_frontend.py' to build the frontend")
        sys.exit(1)
    
    print(f"✅ Static directory found: {static_dir}")
    
    # Test API endpoints
    if not test_api_endpoints(base_url):
        print("❌ API endpoints test failed")
        sys.exit(1)
    
    # Test static files
    if not test_static_files(base_url):
        print("❌ Static files test failed")
        sys.exit(1)
    
    # Test chat functionality
    test_chat_functionality(base_url)
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print(f"🌐 Frontend: {base_url}")
    print(f"📚 API Docs: {base_url}/docs")
    print(f"⚙️  Config: {base_url}/api/config")

if __name__ == "__main__":
    main() 