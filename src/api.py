from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
from typing import List, Dict, Any

from .models import (
    ChatRequest, 
    ChatResponse, 
    Message, 
    HealthResponse,
    AssistantResponse
)
from .agent_manager import agent_manager
from .config import Config
from .task_types import TaskType, TaskConfiguration


app = FastAPI(
    title="Qwen-Agent Chatbot API",
    description="A chatbot API powered by Qwen-Agent framework",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint for non-streaming responses."""
    try:
        # Convert messages to the format expected by Qwen-Agent
        messages = [{"role": msg.role.value, "content": msg.content} for msg in request.messages]
        
        # Create or get agent
        agent_id = "default"  # You could make this configurable
        agent = agent_manager.get_agent(agent_id)
        
        if not agent:
            # Create a new agent with the provided configuration
            agent = agent_manager.create_agent(
                agent_id=agent_id,
                system_message=request.system_message,
                tools=request.tools,
                files=request.files,
                model_config=request.model_config
            )
        
        # Get response
        responses = agent_manager.chat(agent_id, messages, stream=False)
        
        # Extract the content from the last assistant message
        content = ""
        for response in responses:
            if response.get("role") == "assistant":
                content = response.get("content", "")
        
        return ChatResponse(content=content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Chat endpoint for streaming responses."""
    try:
        # Convert messages to the format expected by Qwen-Agent
        messages = [{"role": msg.role.value, "content": msg.content} for msg in request.messages]
        
        # Create or get agent
        agent_id = "default"
        agent = agent_manager.get_agent(agent_id)
        
        if not agent:
            # Create a new agent with the provided configuration
            agent = agent_manager.create_agent(
                agent_id=agent_id,
                system_message=request.system_message,
                tools=request.tools,
                files=request.files,
                model_config=request.model_config
            )
        
        def generate():
            try:
                for response in agent_manager.chat(agent_id, messages, stream=True):
                    yield f"data: {json.dumps(response)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            finally:
                yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents", response_model=Dict[str, Any])
async def create_agent(request: ChatRequest):
    """Create a new agent instance."""
    try:
        agent_id = f"agent_{len(agent_manager.list_agents()) + 1}"
        
        agent = agent_manager.create_agent(
            agent_id=agent_id,
            system_message=request.system_message,
            tools=request.tools,
            files=request.files,
            model_config=request.model_config
        )
        
        return {
            "agent_id": agent_id,
            "status": "created",
            "message": f"Agent {agent_id} created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents", response_model=List[str])
async def list_agents():
    """List all agent IDs."""
    return agent_manager.list_agents()


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent instance."""
    try:
        success = agent_manager.remove_agent(agent_id)
        if success:
            return {"message": f"Agent {agent_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks", response_model=List[Dict[str, Any]])
async def list_tasks():
    """List all available task types."""
    try:
        tasks = []
        for task_type in agent_manager.get_available_tasks():
            task_info = agent_manager.get_task_info(task_type)
            if task_info:
                tasks.append({
                    "task_type": task_type.value,
                    "name": task_info.name,
                    "description": task_info.description,
                    "tools": task_info.tools,
                    "tags": task_info.tags
                })
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/{task_type}", response_model=Dict[str, Any])
async def get_task_info(task_type: str):
    """Get detailed information about a specific task type."""
    try:
        try:
            task_enum = TaskType(task_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid task type: {task_type}")
        
        task_info = agent_manager.get_task_info(task_enum)
        if not task_info:
            raise HTTPException(status_code=404, detail=f"Task type {task_type} not found")
        
        return {
            "task_type": task_info.task_type.value,
            "name": task_info.name,
            "description": task_info.description,
            "system_message": task_info.system_message,
            "tools": task_info.tools,
            "tags": task_info.tags,
            "temperature": task_info.temperature,
            "top_p": task_info.top_p,
            "max_tokens": task_info.max_tokens
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/{agent_id}/task", response_model=Dict[str, Any])
async def switch_agent_task(agent_id: str, task_type: str, files: Optional[List[str]] = None):
    """Switch an agent to a specific task type."""
    try:
        try:
            task_enum = TaskType(task_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid task type: {task_type}")
        
        agent = agent_manager.switch_agent_task(agent_id, task_enum, files)
        
        return {
            "agent_id": agent_id,
            "task_type": task_type,
            "status": "switched",
            "message": f"Agent {agent_id} switched to {task_type} task"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/task/{task_type}", response_model=ChatResponse)
async def chat_with_task(task_type: str, request: ChatRequest):
    """Chat with an agent configured for a specific task type."""
    try:
        try:
            task_enum = TaskType(task_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid task type: {task_type}")
        
        # Convert messages to the format expected by Qwen-Agent
        messages = [{"role": msg.role.value, "content": msg.content} for msg in request.messages]
        
        # Create a temporary agent for this task
        temp_agent_id = f"temp_{task_type}_{len(agent_manager.list_agents())}"
        agent = agent_manager.create_task_agent(
            temp_agent_id, 
            task_enum, 
            request.files,
            request.model_config
        )
        
        # Get response
        responses = agent_manager.chat(temp_agent_id, messages, stream=False)
        
        # Extract the content from the last assistant message
        content = ""
        for response in responses:
            if response.get("role") == "assistant":
                content = response.get("content", "")
        
        # Clean up temporary agent
        agent_manager.remove_agent(temp_agent_id)
        
        return ChatResponse(content=content)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    ) 