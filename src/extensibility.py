"""
Extensibility and Security Framework for Qwen-Agent Chatbot

This module provides interfaces for adding custom tools, security guidelines,
and configuration management for the chatbot system.

📚 Documentation:
- Extensibility Guide: docs/EXTENSIBILITY_GUIDE.md
- Security Features: docs/EXTENSIBILITY_GUIDE.md#security-implementation
- Custom Tools: docs/EXTENSIBILITY_GUIDE.md#creating-custom-tools

🔗 Quick Navigation:
- python -m src.doc_cli doc extensibility
- python -m src.doc_cli source extensibility
- python -m src.doc_cli github extensibility
- python -m src.doc_cli search "custom tools"
"""

import os
import json
import logging
import time
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import traceback
from functools import wraps
import inspect

from pydantic import BaseModel, Field, validator
from qwen_agent.tools.base import BaseTool, register_tool


# Configure logging
logger = logging.getLogger(__name__)


class SecurityLevel(str, Enum):
    """Security levels for tools and operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    RESTRICTED = "restricted"


class ToolCategory(str, Enum):
    """Categories for organizing tools."""
    UTILITY = "utility"
    DATA_PROCESSING = "data_processing"
    EXTERNAL_API = "external_api"
    FILE_OPERATIONS = "file_operations"
    CODE_EXECUTION = "code_execution"
    NETWORK = "network"
    CUSTOM = "custom"


@dataclass
class ToolMetadata:
    """Metadata for tool registration and management."""
    name: str
    description: str
    category: ToolCategory
    security_level: SecurityLevel
    version: str = "1.0.0"
    author: str = "Unknown"
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None


class ToolConfiguration(BaseModel):
    """Configuration schema for tools."""
    enabled: bool = True
    timeout: int = 30
    max_retries: int = 3
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    allowed_domains: List[str] = Field(default_factory=list)
    blocked_domains: List[str] = Field(default_factory=list)
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = Field(default_factory=list)
    blocked_file_types: List[str] = Field(default_factory=list)
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v < 1 or v > 300:
            raise ValueError('Timeout must be between 1 and 300 seconds')
        return v
    
    @validator('max_retries')
    def validate_max_retries(cls, v):
        if v < 0 or v > 10:
            raise ValueError('Max retries must be between 0 and 10')
        return v


class SecurityContext:
    """Context for security validation and monitoring."""
    
    def __init__(self, user_id: Optional[str] = None, session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id
        self.start_time = time.time()
        self.operations: List[Dict[str, Any]] = []
        self.resource_usage = {
            'cpu_time': 0.0,
            'memory_usage': 0.0,
            'file_operations': 0,
            'network_requests': 0
        }
    
    def log_operation(self, operation: str, details: Dict[str, Any]):
        """Log an operation for audit purposes."""
        self.operations.append({
            'timestamp': time.time(),
            'operation': operation,
            'details': details
        })
    
    def get_execution_time(self) -> float:
        """Get total execution time."""
        return time.time() - self.start_time


class SecurityValidator:
    """Validates operations based on security policies."""
    
    def __init__(self, config: ToolConfiguration):
        self.config = config
    
    def validate_file_access(self, file_path: str, operation: str) -> bool:
        """Validate file access permissions."""
        try:
            path = Path(file_path).resolve()
            
            # Check file size
            if path.exists() and path.stat().st_size > self.config.max_file_size:
                logger.warning(f"File {file_path} exceeds size limit")
                return False
            
            # Check file type
            file_ext = path.suffix.lower()
            if self.config.blocked_file_types and file_ext in self.config.blocked_file_types:
                logger.warning(f"File type {file_ext} is blocked")
                return False
            
            if self.config.allowed_file_types and file_ext not in self.config.allowed_file_types:
                logger.warning(f"File type {file_ext} is not allowed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"File access validation failed: {e}")
            return False
    
    def validate_network_request(self, url: str) -> bool:
        """Validate network request permissions."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check blocked domains
            if self.config.blocked_domains and domain in self.config.blocked_domains:
                logger.warning(f"Domain {domain} is blocked")
                return False
            
            # Check allowed domains
            if self.config.allowed_domains and domain not in self.config.allowed_domains:
                logger.warning(f"Domain {domain} is not allowed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Network request validation failed: {e}")
            return False


class CustomToolBase(BaseTool, ABC):
    """Base class for custom tools with security and monitoring."""
    
    def __init__(self, config: Optional[ToolConfiguration] = None):
        super().__init__()
        self.config = config or ToolConfiguration()
        self.security_validator = SecurityValidator(self.config)
        self.metadata = self._get_metadata()
    
    @abstractmethod
    def _get_metadata(self) -> ToolMetadata:
        """Return tool metadata. Must be implemented by subclasses."""
        pass
    
    def _validate_security(self, security_context: SecurityContext, **kwargs) -> bool:
        """Validate security requirements before execution."""
        # Check execution time
        if security_context.get_execution_time() > self.config.timeout:
            logger.warning(f"Tool execution timeout exceeded")
            return False
        
        # Log operation
        security_context.log_operation(
            f"{self.metadata.name}_execution",
            {'kwargs': kwargs, 'timestamp': time.time()}
        )
        
        return True
    
    def _handle_error(self, error: Exception, security_context: SecurityContext):
        """Handle and log errors."""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'timestamp': time.time()
        }
        
        security_context.log_operation(f"{self.metadata.name}_error", error_info)
        logger.error(f"Tool {self.metadata.name} error: {error}")
        
        return f"Error in {self.metadata.name}: {str(error)}"
    
    def call(self, params: str, **kwargs) -> str:
        """Execute the tool with security validation."""
        security_context = SecurityContext()
        
        try:
            # Validate security
            if not self._validate_security(security_context, **kwargs):
                return f"Security validation failed for {self.metadata.name}"
            
            # Execute the tool
            result = self._execute(params, security_context, **kwargs)
            
            # Log successful execution
            security_context.log_operation(
                f"{self.metadata.name}_success",
                {'result_length': len(str(result)), 'timestamp': time.time()}
            )
            
            return result
            
        except Exception as e:
            return self._handle_error(e, security_context)
    
    @abstractmethod
    def _execute(self, params: str, security_context: SecurityContext, **kwargs) -> str:
        """Execute the tool logic. Must be implemented by subclasses."""
        pass


class ToolRegistry:
    """Registry for managing custom tools."""
    
    def __init__(self):
        self._tools: Dict[str, CustomToolBase] = {}
        self._metadata: Dict[str, ToolMetadata] = {}
        self._configurations: Dict[str, ToolConfiguration] = {}
    
    def register_tool(self, tool: CustomToolBase) -> bool:
        """Register a custom tool."""
        try:
            metadata = tool.metadata
            tool_name = metadata.name
            
            if tool_name in self._tools:
                logger.warning(f"Tool {tool_name} already registered, overwriting")
            
            self._tools[tool_name] = tool
            self._metadata[tool_name] = metadata
            self._configurations[tool_name] = tool.config
            
            # Register with Qwen-Agent
            register_tool(tool_name)(tool)
            
            logger.info(f"Tool {tool_name} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register tool {tool_name}: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a custom tool."""
        try:
            if tool_name in self._tools:
                del self._tools[tool_name]
                del self._metadata[tool_name]
                del self._configurations[tool_name]
                logger.info(f"Tool {tool_name} unregistered successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister tool {tool_name}: {e}")
            return False
    
    def get_tool(self, tool_name: str) -> Optional[CustomToolBase]:
        """Get a registered tool."""
        return self._tools.get(tool_name)
    
    def get_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get tool metadata."""
        return self._metadata.get(tool_name)
    
    def list_tools(self, category: Optional[ToolCategory] = None) -> List[str]:
        """List registered tools, optionally filtered by category."""
        if category:
            return [
                name for name, metadata in self._metadata.items()
                if metadata.category == category
            ]
        return list(self._tools.keys())
    
    def get_tools_by_security_level(self, security_level: SecurityLevel) -> List[str]:
        """Get tools by security level."""
        return [
            name for name, metadata in self._metadata.items()
            if metadata.security_level == security_level
        ]


# Global tool registry instance
tool_registry = ToolRegistry()


def register_custom_tool(
    name: str,
    description: str,
    category: ToolCategory = ToolCategory.CUSTOM,
    security_level: SecurityLevel = SecurityLevel.MEDIUM,
    config: Optional[ToolConfiguration] = None
):
    """Decorator for registering custom tools."""
    def decorator(cls):
        if not issubclass(cls, CustomToolBase):
            raise ValueError(f"Class {cls.__name__} must inherit from CustomToolBase")
        
        # Create metadata
        metadata = ToolMetadata(
            name=name,
            description=description,
            category=category,
            security_level=security_level
        )
        
        # Create tool instance
        tool_config = config or ToolConfiguration()
        tool_instance = cls(tool_config)
        tool_instance.metadata = metadata
        
        # Register the tool
        tool_registry.register_tool(tool_instance)
        
        return cls
    
    return decorator


# Example custom tool implementation
@register_custom_tool(
    name="text_processor",
    description="Process and analyze text content",
    category=ToolCategory.DATA_PROCESSING,
    security_level=SecurityLevel.LOW
)
class TextProcessorTool(CustomToolBase):
    """Example custom tool for text processing."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="text_processor",
            description="Process and analyze text content",
            category=ToolCategory.DATA_PROCESSING,
            security_level=SecurityLevel.LOW,
            version="1.0.0",
            author="System",
            tags=["text", "processing", "analysis"]
        )
    
    def _execute(self, params: str, security_context: SecurityContext, **kwargs) -> str:
        """Execute text processing logic."""
        try:
            # Simple text analysis
            words = params.split()
            word_count = len(words)
            char_count = len(params)
            
            result = {
                'word_count': word_count,
                'character_count': char_count,
                'average_word_length': char_count / word_count if word_count > 0 else 0,
                'processed_text': params.upper()
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            raise Exception(f"Text processing failed: {e}")


# Configuration management
class ConfigurationManager:
    """Manages configuration for tools and security settings."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "tool_config.json"
        self.configurations: Dict[str, ToolConfiguration] = {}
        self.load_configurations()
    
    def load_configurations(self):
        """Load configurations from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for tool_name, config_data in data.items():
                        self.configurations[tool_name] = ToolConfiguration(**config_data)
                logger.info(f"Loaded configurations from {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
    
    def save_configurations(self):
        """Save configurations to file."""
        try:
            data = {
                name: config.dict() for name, config in self.configurations.items()
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved configurations to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configurations: {e}")
    
    def get_configuration(self, tool_name: str) -> Optional[ToolConfiguration]:
        """Get configuration for a tool."""
        return self.configurations.get(tool_name)
    
    def set_configuration(self, tool_name: str, config: ToolConfiguration):
        """Set configuration for a tool."""
        self.configurations[tool_name] = config
        self.save_configurations()
    
    def update_configuration(self, tool_name: str, **kwargs):
        """Update configuration for a tool."""
        if tool_name in self.configurations:
            current_config = self.configurations[tool_name]
            updated_config = current_config.copy(update=kwargs)
            self.configurations[tool_name] = updated_config
            self.save_configurations()


# Global configuration manager instance
config_manager = ConfigurationManager()


# Security monitoring and logging
class SecurityMonitor:
    """Monitors security events and provides audit trails."""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or "security_audit.log"
        self.events: List[Dict[str, Any]] = []
    
    def log_event(self, event_type: str, details: Dict[str, Any], user_id: Optional[str] = None):
        """Log a security event."""
        event = {
            'timestamp': time.time(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details
        }
        
        self.events.append(event)
        
        # Write to log file
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.error(f"Failed to write to security log: {e}")
    
    def get_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get security events, optionally filtered by type."""
        events = self.events
        if event_type:
            events = [e for e in events if e['event_type'] == event_type]
        return events[-limit:]
    
    def clear_events(self):
        """Clear stored events."""
        self.events.clear()


# Global security monitor instance
security_monitor = SecurityMonitor()


# Utility functions for developers
def create_tool_template(tool_name: str, category: ToolCategory) -> str:
    """Generate a template for creating new tools."""
    template = f'''
@register_custom_tool(
    name="{tool_name}",
    description="Description of what this tool does",
    category=ToolCategory.{category.upper()},
    security_level=SecurityLevel.MEDIUM
)
class {tool_name.title().replace('_', '')}Tool(CustomToolBase):
    """Custom tool for {tool_name}."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="{tool_name}",
            description="Description of what this tool does",
            category=ToolCategory.{category.upper()},
            security_level=SecurityLevel.MEDIUM,
            version="1.0.0",
            author="Your Name",
            tags=["custom", "{tool_name}"]
        )
    
    def _execute(self, params: str, security_context: SecurityContext, **kwargs) -> str:
        """Execute {tool_name} logic."""
        try:
            # TODO: Implement your tool logic here
            # Example:
            # result = self._process_data(params)
            # return json.dumps(result, indent=2)
            
            return f"Tool {tool_name} executed with params: {{params}}"
            
        except Exception as e:
            raise Exception(f"{tool_name} execution failed: {{e}}")
'''
    return template


def validate_tool_implementation(tool_class: type) -> List[str]:
    """Validate a tool implementation and return any issues."""
    issues = []
    
    if not issubclass(tool_class, CustomToolBase):
        issues.append("Tool class must inherit from CustomToolBase")
    
    # Check required methods
    required_methods = ['_get_metadata', '_execute']
    for method in required_methods:
        if not hasattr(tool_class, method):
            issues.append(f"Missing required method: {method}")
    
    # Check metadata implementation
    if hasattr(tool_class, '_get_metadata'):
        try:
            instance = tool_class()
            metadata = instance._get_metadata()
            if not isinstance(metadata, ToolMetadata):
                issues.append("_get_metadata must return ToolMetadata instance")
        except Exception as e:
            issues.append(f"Error in _get_metadata: {e}")
    
    return issues 