from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    system_message: Optional[str] = None
    tools: Optional[List[str]] = None
    files: Optional[List[str]] = None
    model_config: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    content: str
    ui_signal: Optional[Dict[str, Any]] = None


class ToolCall(BaseModel):
    name: str
    parameters: Dict[str, Any]


class AssistantResponse(BaseModel):
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    ui_signal: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "0.1.0" 