#!/usr/bin/env python3
"""
Test script for the Task Segmentation functionality
"""

import requests
import json
import time


def test_list_tasks():
    """Test listing all available task types."""
    print("Testing task listing...")
    try:
        response = requests.get("http://localhost:8002/tasks")
        if response.status_code == 200:
            print("✅ Task listing test passed")
            tasks = response.json()
            print(f"Found {len(tasks)} task types:")
            for task in tasks:
                print(f"  - {task['name']} ({task['task_type']}): {task['description']}")
                print(f"    Tools: {task['tools']}")
                print(f"    Tags: {task['tags']}")
        else:
            print(f"❌ Task listing test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Task listing test error: {e}")


def test_task_info():
    """Test getting detailed information about a specific task."""
    print("\nTesting task info retrieval...")
    try:
        # Test with code execution task
        response = requests.get("http://localhost:8002/tasks/code_execution")
        if response.status_code == 200:
            print("✅ Task info test passed")
            task_info = response.json()
            print(f"Task: {task_info['name']}")
            print(f"Description: {task_info['description']}")
            print(f"Temperature: {task_info['temperature']}")
            print(f"Tools: {task_info['tools']}")
        else:
            print(f"❌ Task info test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Task info test error: {e}")


def test_task_based_chat():
    """Test chatting with a task-specific agent."""
    print("\nTesting task-based chat...")
    try:
        # Test code execution task
        response = requests.post("http://localhost:8002/chat/task/code_execution", json={
            "messages": [
                {"role": "user", "content": "Write a Python function to calculate the factorial of a number."}
            ]
        })
        
        if response.status_code == 200:
            print("✅ Task-based chat test passed")
            result = response.json()
            print(f"Response: {result['content'][:200]}...")
        else:
            print(f"❌ Task-based chat test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Task-based chat test error: {e}")


def test_agent_task_switching():
    """Test switching an agent to a different task type."""
    print("\nTesting agent task switching...")
    try:
        # First create an agent
        create_response = requests.post("http://localhost:8002/agents", json={
            "messages": [],
            "system_message": "You are a general assistant."
        })
        
        if create_response.status_code == 200:
            agent_data = create_response.json()
            agent_id = agent_data['agent_id']
            print(f"Created agent: {agent_id}")
            
            # Switch to math solving task
            switch_response = requests.post(f"http://localhost:8002/agents/{agent_id}/task", 
                                          params={"task_type": "math_solving"})
            
            if switch_response.status_code == 200:
                print("✅ Agent task switching test passed")
                switch_data = switch_response.json()
                print(f"Switched to: {switch_data['task_type']}")
            else:
                print(f"❌ Agent task switching test failed: {switch_response.status_code}")
                print(f"Error: {switch_response.text}")
        else:
            print(f"❌ Agent creation failed: {create_response.status_code}")
            
    except Exception as e:
        print(f"❌ Agent task switching test error: {e}")


def test_invalid_task():
    """Test handling of invalid task types."""
    print("\nTesting invalid task handling...")
    try:
        response = requests.get("http://localhost:8002/tasks/invalid_task_type")
        if response.status_code == 400:
            print("✅ Invalid task handling test passed")
            print(f"Error message: {response.json()['detail']}")
        else:
            print(f"❌ Invalid task handling test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid task handling test error: {e}")


def main():
    """Run all task segmentation tests."""
    print("🚀 Starting Task Segmentation Tests")
    print("=" * 50)
    
    # Wait a moment for the server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    test_list_tasks()
    test_task_info()
    test_task_based_chat()
    test_agent_task_switching()
    test_invalid_task()
    
    print("\n" + "=" * 50)
    print("🏁 Task segmentation tests completed!")


if __name__ == "__main__":
    main() 