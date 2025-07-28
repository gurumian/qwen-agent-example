#!/usr/bin/env python3
"""
Test script for the Web Interface functionality
"""

import requests
import time
import json
from pathlib import Path


def test_webui_connection():
    """Test if the web interface is accessible."""
    print("Testing WebUI connection...")
    try:
        # Test if the API server is running
        response = requests.get("http://localhost:8002/health")
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        return False


def test_task_loading():
    """Test if tasks can be loaded for the web interface."""
    print("\nTesting task loading...")
    try:
        response = requests.get("http://localhost:8002/tasks")
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ Loaded {len(tasks)} tasks")
            for task in tasks:
                print(f"  - {task['name']}: {task['description']}")
            return True
        else:
            print(f"❌ Failed to load tasks: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error loading tasks: {e}")
        return False


def test_chat_functionality():
    """Test basic chat functionality."""
    print("\nTesting chat functionality...")
    try:
        response = requests.post("http://localhost:8002/chat", json={
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ]
        })
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat functionality working")
            print(f"Response: {result['content'][:100]}...")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False


def test_multimodal_chat():
    """Test multi-modal chat functionality."""
    print("\nTesting multi-modal chat...")
    try:
        response = requests.post("http://localhost:8002/chat", json={
            "messages": [
                {"role": "user", "content": "Test message with multi-modal enabled"}
            ],
            "multimodal": True
        })
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Multi-modal chat working")
            if result.get('media'):
                print(f"Media items: {len(result['media'])}")
            return True
        else:
            print(f"❌ Multi-modal chat failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Multi-modal chat error: {e}")
        return False


def test_task_switching():
    """Test task switching functionality."""
    print("\nTesting task switching...")
    try:
        # Switch to code execution task
        response = requests.post("http://localhost:8002/agents/test_user/task", 
                               params={"task_type": "code_execution"})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Task switching working")
            print(f"Switched to: {result['task_type']}")
            return True
        else:
            print(f"❌ Task switching failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Task switching error: {e}")
        return False


def test_file_upload():
    """Test file upload functionality."""
    print("\nTesting file upload...")
    try:
        # Create a test file
        test_file = Path("test_upload.txt")
        test_content = "This is a test file for upload."
        test_file.write_text(test_content)
        
        # Upload the file
        with open(test_file, "rb") as f:
            files = {"file": ("test_upload.txt", f, "text/plain")}
            response = requests.post("http://localhost:8002/multimodal/upload", files=files)
        
        # Clean up test file
        test_file.unlink(missing_ok=True)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ File upload working")
            print(f"Uploaded: {result['filename']}")
            return True
        else:
            print(f"❌ File upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ File upload error: {e}")
        return False


def test_analytics_endpoints():
    """Test analytics and reporting endpoints."""
    print("\nTesting analytics endpoints...")
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8002/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test agents endpoint
        response = requests.get("http://localhost:8002/agents")
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Agents endpoint working ({len(agents)} agents)")
        else:
            print(f"❌ Agents endpoint failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Analytics endpoints error: {e}")
        return False


def main():
    """Run all web interface tests."""
    print("🚀 Starting Web Interface Tests")
    print("=" * 50)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        test_webui_connection,
        test_task_loading,
        test_chat_functionality,
        test_multimodal_chat,
        test_task_switching,
        test_file_upload,
        test_analytics_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 Web Interface Tests Completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Web interface is ready.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main() 