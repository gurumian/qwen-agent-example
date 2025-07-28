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


class TaskInfo(BaseModel):
    task_type: str
    name: str
    description: str
    tools: List[str]
    tags: List[str]


class TaskDetail(BaseModel):
    task_type: str
    name: str
    description: str
    system_message: str
    tools: List[str]
    tags: List[str]
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None


class TaskSwitchRequest(BaseModel):
    task_type: str
    files: Optional[List[str]] = None


class TaskSwitchResponse(BaseModel):
    agent_id: str
    task_type: str
    status: str
    message: str 