import gradio as gr
import requests
import json
import time
import base64
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from .config import Config
from .task_types import TaskType


class ChatbotWebUI:
    """Gradio WebUI for the Qwen-Agent Chatbot."""
    
    def __init__(self):
        self.api_url = f"http://{Config.HOST}:{Config.PORT}"
        self.chat_history = []
        self.current_task = TaskType.GENERAL_CHAT
        self.available_tasks = []
        self.agent_id = "webui_user"
        
        # Initialize available tasks
        self._load_available_tasks()
    
    def _load_available_tasks(self):
        """Load available task types from the API."""
        try:
            response = requests.get(f"{self.api_url}/tasks")
            if response.status_code == 200:
                self.available_tasks = response.json()
            else:
                self.available_tasks = []
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.available_tasks = []
    
    def _get_task_names(self) -> List[str]:
        """Get list of task names for the dropdown."""
        return [task["name"] for task in self.available_tasks]
    
    def _get_task_by_name(self, task_name: str) -> Optional[Dict[str, Any]]:
        """Get task configuration by name."""
        for task in self.available_tasks:
            if task["name"] == task_name:
                return task
        return None
    
    def _switch_task(self, task_name: str) -> str:
        """Switch to a different task type."""
        try:
            task_config = self._get_task_by_name(task_name)
            if not task_config:
                return f"❌ Task '{task_name}' not found"
            
            task_type = task_config["task_type"]
            response = requests.post(
                f"{self.api_url}/agents/{self.agent_id}/task",
                params={"task_type": task_type}
            )
            
            if response.status_code == 200:
                self.current_task = TaskType(task_type)
                return f"✅ Switched to {task_name} task"
            else:
                return f"❌ Failed to switch task: {response.text}"
                
        except Exception as e:
            return f"❌ Error switching task: {e}"
    
    def _process_message(self, message: str, history: List[List[str]], 
                        task_name: str, multimodal: bool = False) -> Tuple[str, List[List[str]]]:
        """Process a chat message and return response."""
        try:
            # Switch task if needed
            if task_name != "General Chat":
                self._switch_task(task_name)
            
            # Prepare the request
            request_data = {
                "messages": [
                    {"role": "user", "content": message}
                ],
                "multimodal": multimodal
            }
            
            # Send request to API
            response = requests.post(f"{self.api_url}/chat", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", "No response received")
                
                # Handle multi-modal response
                if result.get("media"):
                    content += "\n\n**Media Content:**\n"
                    for i, media in enumerate(result["media"], 1):
                        content += f"{i}. {media['type']} ({media['source']})\n"
                
                # Handle UI signals
                if result.get("ui_signal"):
                    content += f"\n\n**UI Signal:** {result['ui_signal']['type']}"
                
                return content, history + [[message, content]]
            else:
                error_msg = f"❌ API Error: {response.status_code} - {response.text}"
                return error_msg, history + [[message, error_msg]]
                
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            return error_msg, history + [[message, error_msg]]
    
    def _process_multimodal_message(self, message: str, files: List[str], 
                                  history: List[List[str]], task_name: str) -> Tuple[str, List[List[str]]]:
        """Process a multi-modal message with file uploads."""
        try:
            # Process uploaded files
            file_info = []
            for file_path in files:
                if file_path and os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        files_data = {"file": (os.path.basename(file_path), f, "application/octet-stream")}
                        upload_response = requests.post(f"{self.api_url}/multimodal/upload", files=files_data)
                        
                        if upload_response.status_code == 200:
                            file_info.append(upload_response.json())
                        else:
                            file_info.append({"error": f"Upload failed: {upload_response.text}"})
            
            # Create multi-modal message
            multimodal_message = message
            if file_info:
                multimodal_message += "\n\n**Uploaded Files:**\n"
                for i, info in enumerate(file_info, 1):
                    if "error" not in info:
                        multimodal_message += f"{i}. {info['filename']} ({info['type']})\n"
                    else:
                        multimodal_message += f"{i}. {info['error']}\n"
            
            # Process the message
            return self._process_message(multimodal_message, history, task_name, multimodal=True)
            
        except Exception as e:
            error_msg = f"❌ Multi-modal processing error: {str(e)}"
            return error_msg, history + [[message, error_msg]]
    
    def _get_task_info(self, task_name: str) -> str:
        """Get detailed information about a task."""
        try:
            task_config = self._get_task_by_name(task_name)
            if not task_config:
                return f"❌ Task '{task_name}' not found"
            
            info = f"**Task: {task_config['name']}**\n\n"
            info += f"**Description:** {task_config['description']}\n\n"
            info += f"**Tools:** {', '.join(task_config['tools']) if task_config['tools'] else 'None'}\n\n"
            info += f"**Tags:** {', '.join(task_config['tags'])}\n\n"
            info += f"**Task Type:** {task_config['task_type']}"
            
            return info
            
        except Exception as e:
            return f"❌ Error getting task info: {e}"
    
    def _create_analytics_dashboard(self) -> go.Figure:
        """Create an analytics dashboard with chat statistics."""
        try:
            # Simple analytics - in a real app, you'd get this from a database
            total_messages = len(self.chat_history)
            user_messages = sum(1 for msg in self.chat_history if msg[0])
            assistant_messages = sum(1 for msg in self.chat_history if msg[1])
            
            # Create a simple bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=['Total Messages', 'User Messages', 'Assistant Messages'],
                    y=[total_messages, user_messages, assistant_messages],
                    marker_color=['blue', 'green', 'orange']
                )
            ])
            
            fig.update_layout(
                title="Chat Analytics",
                xaxis_title="Message Types",
                yaxis_title="Count",
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            # Return empty figure if analytics fail
            fig = go.Figure()
            fig.add_annotation(
                text=f"Analytics Error: {e}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def _export_chat_history(self, history: List[List[str]]) -> str:
        """Export chat history to a formatted string."""
        if not history:
            return "No chat history to export"
        
        export_text = f"# Chat History Export\n"
        export_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_text += f"Current Task: {self.current_task.value}\n\n"
        
        for i, (user_msg, assistant_msg) in enumerate(history, 1):
            export_text += f"## Message {i}\n\n"
            export_text += f"**User:** {user_msg}\n\n"
            export_text += f"**Assistant:** {assistant_msg}\n\n"
            export_text += "---\n\n"
        
        return export_text
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        with gr.Blocks(
            title="Qwen-Agent Chatbot",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1200px !important;
                margin: auto !important;
            }
            .chat-container {
                height: 600px;
                overflow-y: auto;
            }
            """
        ) as interface:
            
            gr.Markdown("# 🤖 Qwen-Agent Chatbot")
            gr.Markdown("A powerful multi-modal chatbot with task segmentation and advanced capabilities.")
            
            with gr.Row():
                with gr.Column(scale=3):
                    # Main chat interface
                    with gr.Group():
                        gr.Markdown("### 💬 Chat Interface")
                        
                        # Task selection
                        task_dropdown = gr.Dropdown(
                            choices=self._get_task_names(),
                            value="General Chat",
                            label="Select Task Type",
                            info="Choose the type of task for the conversation"
                        )
                        
                        # Chat history
                        chatbot = gr.Chatbot(
                            label="Chat History",
                            height=400,
                            show_label=True,
                            container=True,
                            bubble_full_width=False
                        )
                        
                        # Message input
                        with gr.Row():
                            msg = gr.Textbox(
                                label="Message",
                                placeholder="Type your message here...",
                                lines=2,
                                scale=4
                            )
                            send_btn = gr.Button("Send", variant="primary", scale=1)
                        
                        # Multi-modal options
                        with gr.Row():
                            multimodal_checkbox = gr.Checkbox(
                                label="Enable Multi-Modal",
                                value=False,
                                info="Process images, documents, and URLs in messages"
                            )
                            clear_btn = gr.Button("Clear Chat", variant="secondary")
                    
                    # File upload for multi-modal
                    with gr.Group():
                        gr.Markdown("### 📁 File Upload (Multi-Modal)")
                        file_upload = gr.File(
                            label="Upload Files",
                            file_count="multiple",
                            file_types=["image", "pdf", "text"],
                            info="Upload images, documents, or text files for processing"
                        )
                        upload_send_btn = gr.Button("Send with Files", variant="primary")
                
                with gr.Column(scale=1):
                    # Sidebar with additional features
                    with gr.Group():
                        gr.Markdown("### ⚙️ Settings & Info")
                        
                        # Task information
                        task_info_btn = gr.Button("Get Task Info", variant="secondary")
                        task_info_output = gr.Markdown("Select a task to see its information.")
                        
                        # Analytics
                        analytics_btn = gr.Button("Show Analytics", variant="secondary")
                        analytics_plot = gr.Plot(label="Chat Analytics")
                        
                        # Export
                        export_btn = gr.Button("Export Chat", variant="secondary")
                        export_output = gr.Textbox(
                            label="Exported Chat History",
                            lines=10,
                            interactive=False
                        )
                        
                        # System info
                        gr.Markdown("### 📊 System Information")
                        system_info = gr.Markdown(f"""
                        **Model:** {Config.DEFAULT_MODEL}
                        **Server:** {Config.MODEL_SERVER_URL}
                        **API URL:** {self.api_url}
                        **Current Agent:** {self.agent_id}
                        """)
            
            # Event handlers
            def send_message(message, history, task_name, multimodal):
                if not message.strip():
                    return "", history
                return self._process_message(message, history, task_name, multimodal)
            
            def send_with_files(message, files, history, task_name):
                if not message.strip() and not files:
                    return "", history
                return self._process_multimodal_message(message, files, history, task_name)
            
            def clear_chat():
                return []
            
            def get_task_info(task_name):
                return self._get_task_info(task_name)
            
            def show_analytics():
                return self._create_analytics_dashboard()
            
            def export_chat(history):
                return self._export_chat_history(history)
            
            # Connect events
            send_btn.click(
                send_message,
                inputs=[msg, chatbot, task_dropdown, multimodal_checkbox],
                outputs=[msg, chatbot]
            )
            
            msg.submit(
                send_message,
                inputs=[msg, chatbot, task_dropdown, multimodal_checkbox],
                outputs=[msg, chatbot]
            )
            
            upload_send_btn.click(
                send_with_files,
                inputs=[msg, file_upload, chatbot, task_dropdown],
                outputs=[msg, chatbot]
            )
            
            clear_btn.click(
                clear_chat,
                outputs=[chatbot]
            )
            
            task_info_btn.click(
                get_task_info,
                inputs=[task_dropdown],
                outputs=[task_info_output]
            )
            
            analytics_btn.click(
                show_analytics,
                outputs=[analytics_plot]
            )
            
            export_btn.click(
                export_chat,
                inputs=[chatbot],
                outputs=[export_output]
            )
            
            # Auto-refresh task list
            def refresh_tasks():
                self._load_available_tasks()
                return gr.Dropdown(choices=self._get_task_names(), value="General Chat")
            
            # Add refresh button
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh Tasks", variant="secondary")
                refresh_btn.click(
                    refresh_tasks,
                    outputs=[task_dropdown]
                )
        
        return interface


def launch_webui(share: bool = False, server_name: str = "0.0.0.0", server_port: int = 7860):
    """Launch the Gradio web interface."""
    webui = ChatbotWebUI()
    interface = webui.create_interface()
    
    print(f"🚀 Launching Gradio WebUI on http://{server_name}:{server_port}")
    print(f"📱 Share URL: {'enabled' if share else 'disabled'}")
    
    interface.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        show_error=True,
        quiet=False
    )


if __name__ == "__main__":
    launch_webui() 