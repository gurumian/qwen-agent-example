import json
from typing import Dict, Any, List, Optional
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool
from qwen_agent.utils.output_beautify import typewriter_print

from .config import Config
from .task_types import TaskManager, TaskType, TaskConfiguration


class AgentManager:
    """Manages Qwen-Agent instances and configurations."""
    
    def __init__(self):
        self.agents: Dict[str, Assistant] = {}
        self.default_config = Config.get_model_config()
        self.task_manager = TaskManager()
    
    def create_agent(
        self,
        agent_id: str,
        system_message: Optional[str] = None,
        tools: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        model_config: Optional[Dict[str, Any]] = None
    ) -> Assistant:
        """Create a new Qwen-Agent instance."""
        
        # Use default values if not provided
        system_message = system_message or Config.DEFAULT_SYSTEM_MESSAGE
        tools = tools or Config.DEFAULT_TOOLS
        files = files or []
        model_config = model_config or self.default_config
        
        # Create the agent
        agent = Assistant(
            llm=model_config,
            system_message=system_message,
            function_list=tools,
            files=files
        )
        
        # Store the agent
        self.agents[agent_id] = agent
        
        return agent
    
    def create_task_agent(
        self,
        agent_id: str,
        task_type: TaskType,
        files: Optional[List[str]] = None,
        model_config: Optional[Dict[str, Any]] = None
    ) -> Assistant:
        """Create an agent configured for a specific task type."""
        
        # Get task configuration
        task_config = self.task_manager.get_task_config(task_type)
        if not task_config:
            raise ValueError(f"Unknown task type: {task_type}")
        
        # Merge model config with task-specific settings
        final_model_config = model_config or self.default_config.copy()
        if task_config.temperature is not None:
            final_model_config.setdefault('generate_cfg', {})['temperature'] = task_config.temperature
        if task_config.top_p is not None:
            final_model_config.setdefault('generate_cfg', {})['top_p'] = task_config.top_p
        if task_config.max_tokens is not None:
            final_model_config.setdefault('generate_cfg', {})['max_tokens'] = task_config.max_tokens
        
        # Create the agent with task-specific configuration
        agent = Assistant(
            llm=final_model_config,
            system_message=task_config.system_message,
            function_list=task_config.tools,
            files=files or []
        )
        
        # Store the agent
        self.agents[agent_id] = agent
        
        return agent
    
    def switch_agent_task(
        self,
        agent_id: str,
        task_type: TaskType,
        files: Optional[List[str]] = None
    ) -> Assistant:
        """Switch an existing agent to a different task type."""
        
        # Get task configuration
        task_config = self.task_manager.get_task_config(task_type)
        if not task_config:
            raise ValueError(f"Unknown task type: {task_type}")
        
        # Get existing agent or create new one
        agent = self.agents.get(agent_id)
        if agent:
            # Update the existing agent's configuration
            # Note: This is a simplified approach. In practice, you might want to create a new agent
            # since Qwen-Agent doesn't support dynamic reconfiguration
            pass
        
        # Create new agent with task configuration
        return self.create_task_agent(agent_id, task_type, files)
    
    def get_available_tasks(self) -> List[TaskType]:
        """Get list of available task types."""
        return self.task_manager.list_task_types()
    
    def get_task_info(self, task_type: TaskType) -> Optional[TaskConfiguration]:
        """Get information about a specific task type."""
        return self.task_manager.get_task_config(task_type)
    
    def get_agent(self, agent_id: str) -> Optional[Assistant]:
        """Get an existing agent by ID."""
        return self.agents.get(agent_id)
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent by ID."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False
    
    def list_agents(self) -> List[str]:
        """List all agent IDs."""
        return list(self.agents.keys())
    
    def chat(
        self,
        agent_id: str,
        messages: List[Dict[str, str]],
        stream: bool = False
    ):
        """Chat with an agent."""
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        if stream:
            return self._stream_chat(agent, messages)
        else:
            return self._non_stream_chat(agent, messages)
    
    def _stream_chat(self, agent: Assistant, messages: List[Dict[str, str]]):
        """Stream chat response."""
        response_plain_text = ""
        for response in agent.run(messages=messages):
            response_plain_text = typewriter_print(response, response_plain_text)
            yield response
    
    def _non_stream_chat(self, agent: Assistant, messages: List[Dict[str, str]]):
        """Non-streaming chat response."""
        responses = []
        for response in agent.run(messages=messages):
            responses.extend(response)
        return responses


# Global agent manager instance
agent_manager = AgentManager() 