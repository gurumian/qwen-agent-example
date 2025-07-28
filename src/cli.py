#!/usr/bin/env python3
"""
Command Line Interface for Qwen-Agent Chatbot
"""

import cmd
import requests
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
from datetime import datetime

from .config import Config
from .task_types import TaskType


class ChatbotCLI(cmd.Cmd):
    """Interactive command-line interface for the chatbot."""
    
    intro = """
🤖 Qwen-Agent Chatbot CLI
========================
Type 'help' for available commands.
Type 'chat' to start a conversation.
Type 'quit' to exit.

Available commands:
- chat: Start interactive chat
- tasks: List available task types
- switch <task>: Switch to a specific task
- info <task>: Get task information
- history: Show chat history
- clear: Clear chat history
- export: Export chat history
- quit/exit: Exit the CLI
"""
    prompt = "🤖 chatbot> "
    
    def __init__(self):
        super().__init__()
        self.api_url = f"http://{Config.HOST}:{Config.PORT}"
        self.chat_history = []
        self.current_task = TaskType.GENERAL_CHAT
        self.agent_id = "cli_user"
        self.available_tasks = []
        
        # Load available tasks
        self._load_available_tasks()
    
    def _load_available_tasks(self):
        """Load available task types from the API."""
        try:
            response = requests.get(f"{self.api_url}/tasks")
            if response.status_code == 200:
                self.available_tasks = response.json()
            else:
                print(f"❌ Failed to load tasks: {response.status_code}")
                self.available_tasks = []
        except Exception as e:
            print(f"❌ Error loading tasks: {e}")
            self.available_tasks = []
    
    def _switch_task(self, task_name: str) -> bool:
        """Switch to a different task type."""
        try:
            # Find task by name
            task_config = None
            for task in self.available_tasks:
                if task["name"].lower() == task_name.lower():
                    task_config = task
                    break
            
            if not task_config:
                print(f"❌ Task '{task_name}' not found")
                return False
            
            task_type = task_config["task_type"]
            response = requests.post(
                f"{self.api_url}/agents/{self.agent_id}/task",
                params={"task_type": task_type}
            )
            
            if response.status_code == 200:
                self.current_task = TaskType(task_type)
                print(f"✅ Switched to {task_config['name']} task")
                return True
            else:
                print(f"❌ Failed to switch task: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error switching task: {e}")
            return False
    
    def _send_message(self, message: str, multimodal: bool = False) -> str:
        """Send a message to the chatbot and return the response."""
        try:
            request_data = {
                "messages": [
                    {"role": "user", "content": message}
                ],
                "multimodal": multimodal,
                "llm_config": None
            }
            
            response = requests.post(f"{self.api_url}/chat", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", "No response received")
                
                # Handle multi-modal response
                if result.get("media"):
                    content += "\n\n📎 Media Content:\n"
                    for i, media in enumerate(result["media"], 1):
                        content += f"  {i}. {media['type']} ({media['source']})\n"
                
                # Handle UI signals
                if result.get("ui_signal"):
                    content += f"\n🔧 UI Signal: {result['ui_signal']['type']}"
                
                return content
            else:
                return f"❌ API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def do_chat(self, arg):
        """Start an interactive chat session."""
        print(f"\n💬 Starting chat session (Task: {self.current_task.value})")
        print("Type 'quit' to exit chat mode, 'help' for commands.\n")
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Exiting chat mode.")
                    break
                elif user_input.lower() == 'help':
                    print("Chat commands:")
                    print("  quit/exit/q: Exit chat mode")
                    print("  task <name>: Switch task type")
                    print("  multimodal: Toggle multi-modal mode")
                    print("  clear: Clear current conversation")
                    continue
                elif user_input.lower().startswith('task '):
                    task_name = user_input[5:].strip()
                    self._switch_task(task_name)
                    continue
                elif user_input.lower() == 'multimodal':
                    # Toggle multimodal mode
                    print("🔄 Multi-modal mode toggled")
                    continue
                elif user_input.lower() == 'clear':
                    self.chat_history = []
                    print("🧹 Chat history cleared")
                    continue
                elif not user_input:
                    continue
                
                # Send message
                print("🤖 Assistant: ", end="", flush=True)
                response = self._send_message(user_input)
                print(response)
                
                # Store in history
                self.chat_history.append([user_input, response])
                
            except KeyboardInterrupt:
                print("\n👋 Chat interrupted.")
                break
            except EOFError:
                print("\n👋 End of input.")
                break
    
    def do_tasks(self, arg):
        """List available task types."""
        if not self.available_tasks:
            print("❌ No tasks available")
            return
        
        print("\n📋 Available Task Types:")
        print("-" * 50)
        for i, task in enumerate(self.available_tasks, 1):
            status = "🟢" if task["task_type"] == self.current_task.value else "⚪"
            print(f"{i}. {status} {task['name']}")
            print(f"   Description: {task['description']}")
            print(f"   Tools: {', '.join(task['tools']) if task['tools'] else 'None'}")
            print(f"   Tags: {', '.join(task['tags'])}")
            print()
    
    def do_switch(self, arg):
        """Switch to a specific task type."""
        if not arg:
            print("❌ Please specify a task name")
            print("Usage: switch <task_name>")
            return
        
        self._switch_task(arg.strip())
    
    def do_info(self, arg):
        """Get detailed information about a task."""
        if not arg:
            print("❌ Please specify a task name")
            print("Usage: info <task_name>")
            return
        
        task_name = arg.strip()
        task_config = None
        
        for task in self.available_tasks:
            if task["name"].lower() == task_name.lower():
                task_config = task
                break
        
        if not task_config:
            print(f"❌ Task '{task_name}' not found")
            return
        
        print(f"\n📖 Task Information: {task_config['name']}")
        print("-" * 50)
        print(f"Description: {task_config['description']}")
        print(f"Task Type: {task_config['task_type']}")
        print(f"Tools: {', '.join(task_config['tools']) if task_config['tools'] else 'None'}")
        print(f"Tags: {', '.join(task_config['tags'])}")
        
        # Get detailed info from API
        try:
            response = requests.get(f"{self.api_url}/tasks/{task_config['task_type']}")
            if response.status_code == 200:
                detailed_info = response.json()
                print(f"System Message: {detailed_info.get('system_message', 'N/A')}")
                if detailed_info.get('temperature'):
                    print(f"Temperature: {detailed_info['temperature']}")
                if detailed_info.get('max_tokens'):
                    print(f"Max Tokens: {detailed_info['max_tokens']}")
        except Exception as e:
            print(f"Could not fetch detailed info: {e}")
    
    def do_history(self, arg):
        """Show chat history."""
        if not self.chat_history:
            print("📝 No chat history")
            return
        
        print(f"\n📝 Chat History ({len(self.chat_history)} messages):")
        print("-" * 50)
        
        for i, (user_msg, assistant_msg) in enumerate(self.chat_history, 1):
            print(f"\n{i}. User: {user_msg}")
            print(f"   Assistant: {assistant_msg[:100]}{'...' if len(assistant_msg) > 100 else ''}")
    
    def do_clear(self, arg):
        """Clear chat history."""
        self.chat_history = []
        print("🧹 Chat history cleared")
    
    def do_export(self, arg):
        """Export chat history to a file."""
        if not self.chat_history:
            print("❌ No chat history to export")
            return
        
        filename = arg.strip() if arg else f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# Chat History Export\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Current Task: {self.current_task.value}\n\n")
                
                for i, (user_msg, assistant_msg) in enumerate(self.chat_history, 1):
                    f.write(f"## Message {i}\n\n")
                    f.write(f"User: {user_msg}\n\n")
                    f.write(f"Assistant: {assistant_msg}\n\n")
                    f.write("---\n\n")
            
            print(f"✅ Chat history exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting chat history: {e}")
    
    def do_status(self, arg):
        """Show current status and system information."""
        print(f"\n📊 System Status:")
        print("-" * 30)
        print(f"API URL: {self.api_url}")
        print(f"Current Task: {self.current_task.value}")
        print(f"Agent ID: {self.agent_id}")
        print(f"Model: {Config.DEFAULT_MODEL}")
        print(f"Model Server: {Config.MODEL_SERVER_URL}")
        print(f"Chat History: {len(self.chat_history)} messages")
        print(f"Available Tasks: {len(self.available_tasks)}")
        
        # Test API connection
        try:
            response = requests.get(f"{self.api_url}/health")
            if response.status_code == 200:
                print("🟢 API Status: Connected")
            else:
                print("🔴 API Status: Error")
        except Exception as e:
            print(f"🔴 API Status: Disconnected ({e})")
    
    def do_refresh(self, arg):
        """Refresh available tasks from the API."""
        print("🔄 Refreshing tasks...")
        self._load_available_tasks()
        print(f"✅ Loaded {len(self.available_tasks)} tasks")
    
    def do_quit(self, arg):
        """Exit the CLI."""
        print("👋 Goodbye!")
        return True
    
    def do_exit(self, arg):
        """Exit the CLI."""
        return self.do_quit(arg)
    
    def default(self, line):
        """Handle unknown commands by treating them as chat messages."""
        if line.strip():
            print("💬 Sending message...")
            response = self._send_message(line)
            print(f"🤖 Assistant: {response}")
            self.chat_history.append([line, response])


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Qwen-Agent Chatbot CLI")
    parser.add_argument("--host", default=Config.HOST, help="API host")
    parser.add_argument("--port", type=int, default=Config.PORT, help="API port")
    parser.add_argument("--task", help="Initial task type")
    parser.add_argument("--message", help="Send a single message and exit")
    
    args = parser.parse_args()
    
    # Update API URL if custom host/port provided
    if args.host != Config.HOST or args.port != Config.PORT:
        Config.HOST = args.host
        Config.PORT = args.port
    
    # Create CLI instance
    cli = ChatbotCLI()
    
    # Set initial task if specified
    if args.task:
        cli._switch_task(args.task)
    
    # Send single message if specified
    if args.message:
        print(f"💬 Sending: {args.message}")
        response = cli._send_message(args.message)
        print(f"🤖 Assistant: {response}")
        return
    
    # Start interactive CLI
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n👋 Interrupted. Goodbye!")


if __name__ == "__main__":
    main() 