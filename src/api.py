from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
from typing import List, Dict, Any, Union, Optional

from .models import (
    ChatRequest, 
    ChatResponse, 
    Message, 
    HealthResponse,
    AssistantResponse,
    MediaItem,
    MultiModalMessage
)
from .agent_manager import agent_manager
from .config import Config
from .task_types import TaskType, TaskConfiguration
from .multimodal import multimodal_processor, multimodal_response


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
        # Process multi-modal input if enabled
        processed_messages = []
        for msg in request.messages:
            if request.multimodal:
                # Process multi-modal content
                processed_content = multimodal_processor.process_input(msg.content)
                processed_messages.append({
                    "role": msg.role.value,
                    "content": processed_content["content"],
                    "media": processed_content.get("media", [])
                })
            else:
                # Standard text processing
                processed_messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
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
                model_config=request.llm_config
            )
        
        # Get response
        responses = agent_manager.chat(agent_id, processed_messages, stream=False)
        
        # Extract the content from the last assistant message
        content = ""
        response_media = []
        for response in responses:
            if response.get("role") == "assistant":
                content = response.get("content", "")
                # Extract any media from response
                if "media" in response:
                    response_media.extend(response["media"])
        
        # Format response with multi-modal support
        if request.multimodal and response_media:
            formatted_response = multimodal_response.format_response(content, response_media)
            return ChatResponse(
                content=formatted_response["content"],
                media=formatted_response.get("media"),
                ui_signal=formatted_response.get("ui_signal")
            )
        else:
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
                model_config=request.llm_config
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
            model_config=request.llm_config
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
            request.llm_config
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


@app.post("/multimodal/process", response_model=Dict[str, Any])
async def process_multimodal_input(request: Dict[str, Any]):
    """Process multi-modal input and return structured data."""
    try:
        # Extract content from request body
        content = request.get("content", request)  # Fallback to entire request if no content field
        result = multimodal_processor.process_input(content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/multimodal/extract-text", response_model=Dict[str, str])
async def extract_text_from_document(file_path: str):
    """Extract text from a document file."""
    try:
        text = multimodal_processor.extract_text_from_document(file_path)
        return {"file_path": file_path, "extracted_text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/multimodal/analyze-image", response_model=Dict[str, Any])
async def analyze_image(image_path: str):
    """Analyze an image and return metadata."""
    try:
        metadata = multimodal_processor.process_image_for_analysis(image_path)
        return {"image_path": image_path, "metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/multimodal/upload", response_model=Dict[str, Any])
async def upload_file(file: UploadFile = File(...)):
    """Upload a file for multi-modal processing."""
    try:
        # Validate file size
        if file.size and file.size > multimodal_processor.max_file_size:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Save file to temp directory
        file_path = multimodal_processor.temp_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the uploaded file
        file_info = {
            "filename": file.filename,
            "file_path": str(file_path),
            "content_type": file.content_type,
            "size": len(content)
        }
        
        # Determine file type and process accordingly
        if file.content_type and 'image' in file.content_type:
            metadata = multimodal_processor.process_image_for_analysis(str(file_path))
            file_info["type"] = "image"
            file_info["metadata"] = metadata
        elif file.content_type and 'pdf' in file.content_type:
            text = multimodal_processor.extract_text_from_document(str(file_path))
            file_info["type"] = "document"
            file_info["extracted_text"] = text
        
        return file_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/multimodal/cleanup")
async def cleanup_temp_files():
    """Clean up temporary files."""
    try:
        multimodal_processor.cleanup_temp_files()
        return {"message": "Temporary files cleaned up successfully"}
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