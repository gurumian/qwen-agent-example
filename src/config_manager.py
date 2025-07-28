"""
Configuration Management System for Qwen-Agent Chatbot

This module provides a comprehensive configuration management system for:
- Security settings
- Tool configurations
- Environment-specific settings
- Configuration validation and schema
- Hot-reload capability
- Configuration backup and versioning
"""

import os
import json
import yaml
import logging
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
import copy
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from pydantic import BaseModel, Field, validator, root_validator
from .extensibility import SecurityLevel, ToolCategory, ToolConfiguration
from .security import SecurityConfig


# Configure logging
logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ConfigSource(str, Enum):
    """Configuration sources."""
    ENV = "environment"
    FILE = "file"
    DATABASE = "database"
    API = "api"


@dataclass
class ConfigMetadata:
    """Metadata for configuration tracking."""
    version: str = "1.0.0"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    author: str = "system"
    description: str = ""
    checksum: str = ""
    source: ConfigSource = ConfigSource.FILE


class SecurityConfiguration(BaseModel):
    """Security configuration schema."""
    # Code execution security
    enable_sandboxing: bool = True
    max_execution_time: int = Field(30, ge=1, le=300)
    max_memory_usage: int = Field(512 * 1024 * 1024, ge=1024 * 1024)  # 512MB
    max_cpu_percent: float = Field(50.0, ge=1.0, le=100.0)
    
    # File access security
    allowed_file_types: List[str] = Field(default_factory=lambda: [
        '.txt', '.md', '.py', '.json', '.csv', '.xml', '.html', '.css', '.js'
    ])
    blocked_file_types: List[str] = Field(default_factory=lambda: [
        '.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.jar'
    ])
    max_file_size: int = Field(10 * 1024 * 1024, ge=1024)  # 10MB
    allowed_directories: List[str] = Field(default_factory=lambda: [
        '/tmp', '/var/tmp', './temp_uploads', './workspace'
    ])
    
    # Network security
    allowed_domains: List[str] = Field(default_factory=list)
    blocked_domains: List[str] = Field(default_factory=lambda: [
        'localhost', '127.0.0.1', '0.0.0.0'
    ])
    max_network_requests: int = Field(10, ge=0, le=100)
    
    # Audit logging
    enable_audit_logging: bool = True
    audit_log_file: str = "security_audit.log"
    max_audit_log_size: int = Field(100 * 1024 * 1024, ge=1024 * 1024)  # 100MB


class ToolConfigurationSchema(BaseModel):
    """Tool configuration schema."""
    name: str
    enabled: bool = True
    timeout: int = Field(30, ge=1, le=300)
    max_retries: int = Field(3, ge=0, le=10)
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    allowed_domains: List[str] = Field(default_factory=list)
    blocked_domains: List[str] = Field(default_factory=list)
    max_file_size: int = Field(10 * 1024 * 1024, ge=1024)
    allowed_file_types: List[str] = Field(default_factory=list)
    blocked_file_types: List[str] = Field(default_factory=list)
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class ModelConfiguration(BaseModel):
    """Model configuration schema."""
    default_model: str = "qwen3:14b"
    default_model_type: str = "oai"
    model_server_url: str = "http://localhost:11434/v1"
    model_server_api_key: str = "EMPTY"
    max_tokens: int = Field(4096, ge=1, le=32768)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    top_p: float = Field(0.9, ge=0.0, le=1.0)
    enable_thinking: bool = False
    use_raw_api: bool = False


class APIConfiguration(BaseModel):
    """API configuration schema."""
    host: str = "0.0.0.0"
    port: int = Field(8002, ge=1024, le=65535)
    debug: bool = False
    workers: int = Field(1, ge=1, le=16)
    max_request_size: int = Field(10 * 1024 * 1024, ge=1024)  # 10MB
    rate_limit_per_minute: int = Field(60, ge=1, le=1000)
    rate_limit_per_hour: int = Field(1000, ge=1, le=10000)
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    enable_metrics: bool = True


class LoggingConfiguration(BaseModel):
    """Logging configuration schema."""
    level: str = Field("INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    max_file_size: int = Field(10 * 1024 * 1024, ge=1024 * 1024)  # 10MB
    backup_count: int = Field(5, ge=0, le=20)
    enable_console: bool = True
    enable_file: bool = False


class MainConfiguration(BaseModel):
    """Main configuration schema."""
    environment: Environment = Environment.DEVELOPMENT
    security: SecurityConfiguration = Field(default_factory=SecurityConfiguration)
    tools: Dict[str, ToolConfigurationSchema] = Field(default_factory=dict)
    model: ModelConfiguration = Field(default_factory=ModelConfiguration)
    api: APIConfiguration = Field(default_factory=APIConfiguration)
    logging: LoggingConfiguration = Field(default_factory=LoggingConfiguration)
    
    @root_validator
    def validate_configuration(cls, values):
        """Validate the entire configuration."""
        # Check for conflicting settings
        security = values.get('security')
        if security and security.enable_sandboxing:
            # Ensure blocked file types don't conflict with allowed types
            blocked = set(security.blocked_file_types)
            allowed = set(security.allowed_file_types)
            conflicts = blocked.intersection(allowed)
            if conflicts:
                raise ValueError(f"Conflicting file types in allowed and blocked lists: {conflicts}")
        
        return values


class ConfigurationManager:
    """Manages configuration for the entire application."""
    
    def __init__(self, config_dir: str = "config", environment: Environment = Environment.DEVELOPMENT):
        self.config_dir = Path(config_dir)
        self.environment = environment
        self.config_file = self.config_dir / f"config_{environment.value}.json"
        self.backup_dir = self.config_dir / "backups"
        self.config: Optional[MainConfiguration] = None
        self.metadata: ConfigMetadata = ConfigMetadata()
        self.observers: List[ConfigurationObserver] = []
        
        # Create directories
        self.config_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.load_configuration()
        
        # Set up file watching for hot reload
        self.setup_file_watcher()
    
    def load_configuration(self, force_reload: bool = False) -> MainConfiguration:
        """Load configuration from file or create default."""
        if self.config is not None and not force_reload:
            return self.config
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.config = MainConfiguration(**data)
                    logger.info(f"Loaded configuration from {self.config_file}")
            else:
                self.config = self.create_default_configuration()
                self.save_configuration()
                logger.info(f"Created default configuration at {self.config_file}")
            
            # Update metadata
            self.metadata.updated_at = time.time()
            self.metadata.checksum = self._calculate_checksum()
            
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = self.create_default_configuration()
            return self.config
    
    def create_default_configuration(self) -> MainConfiguration:
        """Create a default configuration."""
        return MainConfiguration(
            environment=self.environment,
            security=SecurityConfiguration(),
            tools={
                "code_interpreter": ToolConfigurationSchema(
                    name="code_interpreter",
                    enabled=True,
                    timeout=30,
                    security_level=SecurityLevel.HIGH
                ),
                "web_search": ToolConfigurationSchema(
                    name="web_search",
                    enabled=True,
                    timeout=60,
                    security_level=SecurityLevel.MEDIUM
                ),
                "image_gen": ToolConfigurationSchema(
                    name="image_gen",
                    enabled=True,
                    timeout=120,
                    security_level=SecurityLevel.MEDIUM
                )
            },
            model=ModelConfiguration(),
            api=APIConfiguration(),
            logging=LoggingConfiguration()
        )
    
    def save_configuration(self, create_backup: bool = True) -> bool:
        """Save configuration to file."""
        try:
            if create_backup and self.config_file.exists():
                self.create_backup()
            
            # Update metadata
            self.metadata.updated_at = time.time()
            self.metadata.checksum = self._calculate_checksum()
            
            # Save configuration
            with open(self.config_file, 'w') as f:
                json.dump(self.config.dict(), f, indent=2)
            
            logger.info(f"Saved configuration to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def create_backup(self) -> str:
        """Create a backup of the current configuration."""
        try:
            timestamp = int(time.time())
            backup_file = self.backup_dir / f"config_backup_{timestamp}.json"
            
            with open(backup_file, 'w') as f:
                json.dump(self.config.dict(), f, indent=2)
            
            logger.info(f"Created configuration backup: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return ""
    
    def restore_backup(self, backup_file: str) -> bool:
        """Restore configuration from backup."""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
            with open(backup_path, 'r') as f:
                data = json.load(f)
                self.config = MainConfiguration(**data)
            
            self.save_configuration(create_backup=False)
            logger.info(f"Restored configuration from backup: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available configuration backups."""
        backups = []
        try:
            for backup_file in self.backup_dir.glob("config_backup_*.json"):
                stat = backup_file.stat()
                backups.append({
                    'file': str(backup_file),
                    'timestamp': stat.st_mtime,
                    'size': stat.st_size,
                    'created_at': time.ctime(stat.st_mtime)
                })
            
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
        
        return backups
    
    def update_configuration(self, **kwargs) -> bool:
        """Update configuration with new values."""
        try:
            if self.config is None:
                self.load_configuration()
            
            # Update configuration
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    logger.warning(f"Unknown configuration key: {key}")
            
            # Validate configuration
            self.config = MainConfiguration(**self.config.dict())
            
            # Save configuration
            return self.save_configuration()
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    def get_tool_configuration(self, tool_name: str) -> Optional[ToolConfigurationSchema]:
        """Get configuration for a specific tool."""
        if self.config is None:
            self.load_configuration()
        
        return self.config.tools.get(tool_name)
    
    def set_tool_configuration(self, tool_name: str, config: ToolConfigurationSchema) -> bool:
        """Set configuration for a specific tool."""
        try:
            if self.config is None:
                self.load_configuration()
            
            self.config.tools[tool_name] = config
            return self.save_configuration()
            
        except Exception as e:
            logger.error(f"Failed to set tool configuration: {e}")
            return False
    
    def update_tool_configuration(self, tool_name: str, **kwargs) -> bool:
        """Update configuration for a specific tool."""
        try:
            if self.config is None:
                self.load_configuration()
            
            if tool_name not in self.config.tools:
                logger.warning(f"Tool {tool_name} not found in configuration")
                return False
            
            current_config = self.config.tools[tool_name]
            updated_config = current_config.copy(update=kwargs)
            self.config.tools[tool_name] = updated_config
            
            return self.save_configuration()
            
        except Exception as e:
            logger.error(f"Failed to update tool configuration: {e}")
            return False
    
    def enable_tool(self, tool_name: str) -> bool:
        """Enable a tool."""
        return self.update_tool_configuration(tool_name, enabled=True)
    
    def disable_tool(self, tool_name: str) -> bool:
        """Disable a tool."""
        return self.update_tool_configuration(tool_name, enabled=False)
    
    def get_security_configuration(self) -> SecurityConfiguration:
        """Get security configuration."""
        if self.config is None:
            self.load_configuration()
        
        return self.config.security
    
    def update_security_configuration(self, **kwargs) -> bool:
        """Update security configuration."""
        try:
            if self.config is None:
                self.load_configuration()
            
            current_security = self.config.security
            updated_security = current_security.copy(update=kwargs)
            self.config.security = updated_security
            
            return self.save_configuration()
            
        except Exception as e:
            logger.error(f"Failed to update security configuration: {e}")
            return False
    
    def get_model_configuration(self) -> ModelConfiguration:
        """Get model configuration."""
        if self.config is None:
            self.load_configuration()
        
        return self.config.model
    
    def update_model_configuration(self, **kwargs) -> bool:
        """Update model configuration."""
        try:
            if self.config is None:
                self.load_configuration()
            
            current_model = self.config.model
            updated_model = current_model.copy(update=kwargs)
            self.config.model = updated_model
            
            return self.save_configuration()
            
        except Exception as e:
            logger.error(f"Failed to update model configuration: {e}")
            return False
    
    def get_api_configuration(self) -> APIConfiguration:
        """Get API configuration."""
        if self.config is None:
            self.load_configuration()
        
        return self.config.api
    
    def update_api_configuration(self, **kwargs) -> bool:
        """Update API configuration."""
        try:
            if self.config is None:
                self.load_configuration()
            
            current_api = self.config.api
            updated_api = current_api.copy(update=kwargs)
            self.config.api = updated_api
            
            return self.save_configuration()
            
        except Exception as e:
            logger.error(f"Failed to update API configuration: {e}")
            return False
    
    def _calculate_checksum(self) -> str:
        """Calculate checksum of current configuration."""
        if self.config is None:
            return ""
        
        config_str = json.dumps(self.config.dict(), sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def setup_file_watcher(self):
        """Set up file watching for hot reload."""
        try:
            self.observer = Observer()
            event_handler = ConfigurationFileHandler(self)
            self.observer.schedule(event_handler, str(self.config_dir), recursive=False)
            self.observer.start()
            logger.info("Configuration file watcher started")
        except Exception as e:
            logger.warning(f"Failed to setup file watcher: {e}")
    
    def add_observer(self, observer: 'ConfigurationObserver'):
        """Add a configuration observer."""
        self.observers.append(observer)
    
    def remove_observer(self, observer: 'ConfigurationObserver'):
        """Remove a configuration observer."""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_observers(self, event_type: str, data: Any = None):
        """Notify all observers of configuration changes."""
        for observer in self.observers:
            try:
                observer.on_configuration_changed(event_type, data)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        if self.config is None:
            self.load_configuration()
        
        return {
            'environment': self.config.environment.value,
            'security_enabled': self.config.security.enable_sandboxing,
            'tools_count': len(self.config.tools),
            'enabled_tools': len([t for t in self.config.tools.values() if t.enabled]),
            'model': self.config.model.default_model,
            'api_port': self.config.api.port,
            'metadata': asdict(self.metadata)
        }


class ConfigurationObserver:
    """Base class for configuration observers."""
    
    def on_configuration_changed(self, event_type: str, data: Any = None):
        """Called when configuration changes."""
        pass


class ConfigurationFileHandler(FileSystemEventHandler):
    """Handles configuration file changes."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
    
    def on_modified(self, event):
        """Called when a file is modified."""
        if not event.is_directory and event.src_path.endswith('.json'):
            logger.info(f"Configuration file changed: {event.src_path}")
            self.config_manager.load_configuration(force_reload=True)
            self.config_manager.notify_observers('file_modified', event.src_path)


# Global configuration manager instance
config_manager = ConfigurationManager()


# Utility functions
def get_config() -> MainConfiguration:
    """Get the current configuration."""
    return config_manager.load_configuration()


def update_config(**kwargs) -> bool:
    """Update configuration."""
    return config_manager.update_configuration(**kwargs)


def get_tool_config(tool_name: str) -> Optional[ToolConfigurationSchema]:
    """Get tool configuration."""
    return config_manager.get_tool_configuration(tool_name)


def update_tool_config(tool_name: str, **kwargs) -> bool:
    """Update tool configuration."""
    return config_manager.update_tool_configuration(tool_name, **kwargs)


def get_security_config() -> SecurityConfiguration:
    """Get security configuration."""
    return config_manager.get_security_configuration()


def update_security_config(**kwargs) -> bool:
    """Update security configuration."""
    return config_manager.update_security_configuration(**kwargs)


def get_model_config() -> ModelConfiguration:
    """Get model configuration."""
    return config_manager.get_model_configuration()


def update_model_config(**kwargs) -> bool:
    """Update model configuration."""
    return config_manager.update_model_configuration(**kwargs)


def get_api_config() -> APIConfiguration:
    """Get API configuration."""
    return config_manager.get_api_configuration()


def update_api_config(**kwargs) -> bool:
    """Update API configuration."""
    return config_manager.update_api_configuration(**kwargs) 