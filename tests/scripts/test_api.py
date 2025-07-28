#!/usr/bin/env python3
"""
Test script for the Qwen-Agent Chatbot API
"""

import requests
import json
import time


def test_health():
    """Test the health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8002/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")


def test_basic_chat():
    """Test basic chat functionality."""
    print("\nTesting basic chat...")
    try:
        response = requests.post("http://localhost:8002/chat", json={
            "messages": [
                {"role": "user", "content": "Hello! Please respond with a simple greeting."}
            ]
        })
        
        if response.status_code == 200:
            print("✅ Basic chat test passed")
            result = response.json()
            print(f"Response: {result['content'][:100]}...")
        else:
            print(f"❌ Basic chat test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Basic chat test error: {e}")


def test_streaming_chat():
    """Test streaming chat functionality."""
    print("\nTesting streaming chat...")
    try:
        response = requests.post("http://localhost:8002/chat/stream", json={
            "messages": [
                {"role": "user", "content": "Count from 1 to 5 slowly."}
            ]
        }, stream=True)
        
        if response.status_code == 200:
            print("✅ Streaming chat test passed")
            print("Streaming response:")
            for line in response.iter_lines():
                if line:
                    data = line.decode('utf-8').replace('data: ', '')
                    if data == '[DONE]':
                        break
                    try:
                        parsed = json.loads(data)
                        if 'content' in parsed:
                            print(parsed['content'], end='', flush=True)
                    except json.JSONDecodeError:
                        pass
            print()
        else:
            print(f"❌ Streaming chat test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Streaming chat test error: {e}")


def test_agent_management():
    """Test agent management endpoints."""
    print("\nTesting agent management...")
    try:
        # List agents
        response = requests.get("http://localhost:8002/agents")
        if response.status_code == 200:
            print("✅ List agents test passed")
            agents = response.json()
            print(f"Current agents: {agents}")
        else:
            print(f"❌ List agents test failed: {response.status_code}")
        
        # Create a new agent
        response = requests.post("http://localhost:8002/agents", json={
            "messages": [],
            "system_message": "You are a helpful math tutor."
        })
        
        if response.status_code == 200:
            print("✅ Create agent test passed")
            result = response.json()
            print(f"Created agent: {result}")
            
            # Delete the agent
            agent_id = result['agent_id']
            delete_response = requests.delete(f"http://localhost:8002/agents/{agent_id}")
            if delete_response.status_code == 200:
                print("✅ Delete agent test passed")
            else:
                print(f"❌ Delete agent test failed: {delete_response.status_code}")
        else:
            print(f"❌ Create agent test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Agent management test error: {e}")


def main():
    """Run all tests."""
    print("🚀 Starting Qwen-Agent Chatbot API Tests")
    print("=" * 50)
    
    # Wait a moment for the server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    test_health()
    test_basic_chat()
    test_streaming_chat()
    test_agent_management()
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")


if __name__ == "__main__":
    main() 