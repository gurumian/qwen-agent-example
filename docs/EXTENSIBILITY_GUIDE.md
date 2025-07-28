# Extensibility and Security Guide

This guide provides comprehensive documentation for extending the Qwen-Agent Chatbot system with custom tools, implementing security measures, and managing configurations.

## Table of Contents

1. [Custom Tool Development](#custom-tool-development)
2. [Security Implementation](#security-implementation)
3. [Configuration Management](#configuration-management)
4. [Best Practices](#best-practices)
5. [Examples](#examples)
6. [Troubleshooting](#troubleshooting)

## Custom Tool Development

### Overview

The extensibility framework provides a standardized way to create custom tools that integrate seamlessly with the Qwen-Agent system. All custom tools inherit from `CustomToolBase` and include built-in security validation and monitoring.

### Creating a Custom Tool

#### Basic Tool Structure

```python
from src.extensibility import (
    CustomToolBase, ToolMetadata, ToolCategory, 
    SecurityLevel, register_custom_tool
)

@register_custom_tool(
    name="my_custom_tool",
    description="Description of what this tool does",
    category=ToolCategory.DATA_PROCESSING,
    security_level=SecurityLevel.MEDIUM
)
class MyCustomTool(CustomToolBase):
    """Custom tool for data processing."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="my_custom_tool",
            description="Description of what this tool does",
            category=ToolCategory.DATA_PROCESSING,
            security_level=SecurityLevel.MEDIUM,
            version="1.0.0",
            author="Your Name",
            tags=["custom", "data", "processing"]
        )
    
    def _execute(self, params: str, security_context: SecurityContext, **kwargs) -> str:
        """Execute the tool logic."""
        try:
            # Your tool implementation here
            result = self._process_data(params)
            return json.dumps(result, indent=2)
            
        except Exception as e:
            raise Exception(f"Tool execution failed: {e}")
    
    def _process_data(self, data: str) -> Dict[str, Any]:
        """Process the input data."""
        # Implement your data processing logic
        return {"processed": data, "status": "success"}
```

#### Tool Categories

Available tool categories:

- `ToolCategory.UTILITY`: General utility tools
- `ToolCategory.DATA_PROCESSING`: Data analysis and processing tools
- `ToolCategory.EXTERNAL_API`: Tools that interact with external APIs
- `ToolCategory.FILE_OPERATIONS`: File handling and manipulation tools
- `ToolCategory.CODE_EXECUTION`: Code execution and analysis tools
- `ToolCategory.NETWORK`: Network-related tools
- `ToolCategory.CUSTOM`: Custom domain-specific tools

#### Security Levels

- `SecurityLevel.LOW`: Minimal security restrictions
- `SecurityLevel.MEDIUM`: Standard security measures
- `SecurityLevel.HIGH`: Strict security controls
- `SecurityLevel.RESTRICTED`: Maximum security restrictions

### Advanced Tool Features

#### Configuration Management

```python
from src.extensibility import ToolConfiguration

# Create custom configuration
config = ToolConfiguration(
    timeout=60,
    max_retries=3,
    security_level=SecurityLevel.HIGH,
    allowed_domains=["api.example.com"],
    max_file_size=5 * 1024 * 1024  # 5MB
)

@register_custom_tool(
    name="advanced_tool",
    description="Advanced tool with custom configuration",
    category=ToolCategory.EXTERNAL_API,
    security_level=SecurityLevel.HIGH,
    config=config
)
class AdvancedTool(CustomToolBase):
    # Tool implementation...
```

#### Error Handling and Logging

```python
def _execute(self, params: str, security_context: SecurityContext, **kwargs) -> str:
    """Execute with comprehensive error handling."""
    try:
        # Log operation start
        security_context.log_operation("tool_start", {"params": params})
        
        # Validate input
        if not params.strip():
            raise ValueError("Empty input provided")
        
        # Process data
        result = self._process_data(params)
        
        # Log successful completion
        security_context.log_operation("tool_success", {"result_size": len(str(result))})
        
        return json.dumps(result, indent=2)
        
    except ValueError as e:
        # Handle validation errors
        security_context.log_operation("tool_validation_error", {"error": str(e)})
        return json.dumps({"error": "validation_error", "message": str(e)})
        
    except Exception as e:
        # Handle unexpected errors
        security_context.log_operation("tool_error", {"error": str(e)})
        raise Exception(f"Tool execution failed: {e}")
```

### Tool Registration and Management

#### Manual Registration

```python
from src.extensibility import tool_registry

# Create tool instance
my_tool = MyCustomTool()

# Register manually
tool_registry.register_tool(my_tool)

# Check if registered
if tool_registry.get_tool("my_custom_tool"):
    print("Tool registered successfully")
```

#### Tool Discovery

```python
# List all registered tools
all_tools = tool_registry.list_tools()

# List tools by category
data_tools = tool_registry.list_tools(ToolCategory.DATA_PROCESSING)

# List tools by security level
high_security_tools = tool_registry.get_tools_by_security_level(SecurityLevel.HIGH)
```

## Security Implementation

### Overview

The security framework provides comprehensive protection for code execution, file access, and network operations. It includes sandboxing, resource monitoring, and audit logging.

### Code Execution Security

#### Sandboxed Execution

```python
from src.security import security_manager, SecurityViolation, ResourceLimitExceeded

try:
    # Execute code safely
    result = security_manager.execute_code_safely(
        code="print('Hello, World!')",
        timeout=30,
        user_id="user123"
    )
    print(f"Execution result: {result}")
    
except SecurityViolation as e:
    print(f"Security violation: {e}")
except ResourceLimitExceeded as e:
    print(f"Resource limit exceeded: {e}")
```

#### Security Decorators

```python
from src.security import secure_code_execution, secure_file_operation, secure_network_request

@secure_code_execution(timeout=60)
def process_data(data: str) -> str:
    # This function will be executed in a sandboxed environment
    return f"Processed: {data}"

@secure_file_operation(operation="read")
def read_file(file_path: str) -> str:
    # This function will validate file access before execution
    with open(file_path, 'r') as f:
        return f.read()

@secure_network_request(method="GET")
def fetch_data(url: str) -> str:
    # This function will validate network requests
    import requests
    response = requests.get(url)
    return response.text
```

### File Access Security

#### File Validation

```python
from src.security import FileSecurityManager

file_manager = FileSecurityManager()

# Validate file access
if file_manager.validate_file_access("/path/to/file.txt", "read"):
    # Safe to read the file
    with open("/path/to/file.txt", "r") as f:
        content = f.read()
else:
    print("File access not allowed")
```

#### Safe Temporary Files

```python
# Create safe temporary file
temp_file = file_manager.create_safe_temp_file(suffix=".txt", prefix="data_")

try:
    # Use the temporary file
    with open(temp_file, 'w') as f:
        f.write("Temporary data")
    
    # Process the file
    # ...
    
finally:
    # Clean up
    file_manager.cleanup_temp_files([temp_file])
```

### Network Security

#### URL Validation

```python
from src.security import NetworkSecurityManager

network_manager = NetworkSecurityManager()

# Validate URL
if network_manager.validate_url("https://api.example.com/data"):
    # Safe to make request
    import requests
    response = requests.get("https://api.example.com/data")
else:
    print("URL not allowed")
```

### Security Monitoring

#### Audit Logging

```python
from src.security import security_monitor

# Log security events
security_monitor.log_event(
    event_type="user_login",
    details={"user_id": "user123", "ip_address": "192.168.1.1"},
    user_id="user123"
)

# Get security events
recent_events = security_monitor.get_events(limit=50)
login_events = security_monitor.get_events(event_type="user_login", limit=10)
```

#### Security Statistics

```python
# Get security statistics
stats = security_manager.get_security_stats()
print(f"Total events: {stats['total_events']}")
print(f"Security violations: {stats['security_violations']}")
```

## Configuration Management

### Overview

The configuration management system provides hierarchical configuration with validation, hot-reload capability, and backup/restore functionality.

### Basic Configuration Usage

#### Loading Configuration

```python
from src.config_manager import get_config, update_config

# Get current configuration
config = get_config()

# Access configuration sections
security_config = config.security
model_config = config.model
api_config = config.api
```

#### Updating Configuration

```python
# Update security configuration
update_security_config(
    enable_sandboxing=True,
    max_execution_time=60,
    max_memory_usage=1024 * 1024 * 1024  # 1GB
)

# Update model configuration
update_model_config(
    default_model="qwen3-235b-a22b",
    temperature=0.5,
    max_tokens=8192
)

# Update API configuration
update_api_config(
    port=8003,
    rate_limit_per_minute=100,
    debug=True
)
```

### Tool Configuration

#### Managing Tool Settings

```python
from src.config_manager import (
    get_tool_config, update_tool_config,
    enable_tool, disable_tool
)

# Get tool configuration
tool_config = get_tool_config("code_interpreter")
print(f"Timeout: {tool_config.timeout}")
print(f"Security level: {tool_config.security_level}")

# Update tool configuration
update_tool_config(
    "code_interpreter",
    timeout=45,
    max_retries=5,
    security_level=SecurityLevel.HIGH
)

# Enable/disable tools
enable_tool("web_search")
disable_tool("image_gen")
```

### Configuration Backup and Restore

```python
from src.config_manager import config_manager

# Create backup
backup_file = config_manager.create_backup()
print(f"Backup created: {backup_file}")

# List backups
backups = config_manager.list_backups()
for backup in backups:
    print(f"Backup: {backup['file']}, Created: {backup['created_at']}")

# Restore from backup
if config_manager.restore_backup(backup_file):
    print("Configuration restored successfully")
```

### Configuration Observers

#### Creating Configuration Observers

```python
from src.config_manager import ConfigurationObserver

class MyConfigObserver(ConfigurationObserver):
    def on_configuration_changed(self, event_type: str, data: Any = None):
        if event_type == "file_modified":
            print(f"Configuration file modified: {data}")
            # Reload your application components
            self.reload_components()

# Register observer
config_manager.add_observer(MyConfigObserver())
```

## Best Practices

### Security Best Practices

1. **Always validate inputs**: Check all user inputs before processing
2. **Use appropriate security levels**: Choose the right security level for your tool
3. **Implement proper error handling**: Catch and handle exceptions gracefully
4. **Log security events**: Use the audit logging system for important events
5. **Limit resource usage**: Set appropriate timeouts and memory limits
6. **Validate file operations**: Always check file paths and types
7. **Restrict network access**: Only allow necessary network operations

### Tool Development Best Practices

1. **Follow the template**: Use the provided tool template structure
2. **Document your tools**: Provide clear descriptions and examples
3. **Handle errors gracefully**: Implement comprehensive error handling
4. **Use appropriate categories**: Choose the right tool category
5. **Test thoroughly**: Test your tools with various inputs
6. **Monitor performance**: Use the resource monitoring features
7. **Keep tools focused**: Each tool should have a single, clear purpose

### Configuration Best Practices

1. **Use environment-specific configs**: Different configs for dev/staging/prod
2. **Validate configurations**: Always validate config changes
3. **Backup before changes**: Create backups before major changes
4. **Use hot-reload carefully**: Test hot-reload functionality thoroughly
5. **Monitor configuration changes**: Use observers to track changes
6. **Document custom settings**: Document any custom configuration options

## Examples

### Complete Custom Tool Example

```python
"""
Example: Data Analysis Tool

This tool demonstrates a complete custom tool implementation
with security, configuration, and error handling.
"""

import json
import pandas as pd
from typing import Dict, Any, List
from src.extensibility import (
    CustomToolBase, ToolMetadata, ToolCategory, 
    SecurityLevel, register_custom_tool, SecurityContext
)
from src.security import secure_file_operation

@register_custom_tool(
    name="data_analyzer",
    description="Analyze CSV data and provide statistical insights",
    category=ToolCategory.DATA_PROCESSING,
    security_level=SecurityLevel.MEDIUM
)
class DataAnalyzerTool(CustomToolBase):
    """Tool for analyzing CSV data files."""
    
    def _get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="data_analyzer",
            description="Analyze CSV data and provide statistical insights",
            category=ToolCategory.DATA_PROCESSING,
            security_level=SecurityLevel.MEDIUM,
            version="1.0.0",
            author="Data Team",
            tags=["data", "analysis", "csv", "statistics"]
        )
    
    def _execute(self, params: str, security_context: SecurityContext, **kwargs) -> str:
        """Execute data analysis."""
        try:
            # Parse parameters
            data = json.loads(params)
            file_path = data.get('file_path')
            
            if not file_path:
                raise ValueError("file_path is required")
            
            # Validate file access
            if not self.security_validator.validate_file_access(file_path, "read"):
                raise SecurityViolation(f"File access not allowed: {file_path}")
            
            # Analyze the data
            result = self._analyze_csv_file(file_path)
            
            # Log successful analysis
            security_context.log_operation(
                "data_analysis_success",
                {"file_path": file_path, "rows_analyzed": result['row_count']}
            )
            
            return json.dumps(result, indent=2)
            
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON parameters")
        except Exception as e:
            security_context.log_operation(
                "data_analysis_error",
                {"error": str(e), "params": params}
            )
            raise Exception(f"Data analysis failed: {e}")
    
    @secure_file_operation(operation="read")
    def _analyze_csv_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a CSV file and return statistics."""
        df = pd.read_csv(file_path)
        
        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'data_types': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_summary': df.describe().to_dict() if df.select_dtypes(include=['number']).shape[1] > 0 else {},
            'file_path': file_path
        }
```

### Security Configuration Example

```python
"""
Example: Custom Security Configuration

This example shows how to configure security settings
for different environments.
"""

from src.config_manager import update_security_config
from src.security import SecurityConfig

# Development environment - relaxed security
def configure_dev_security():
    update_security_config(
        enable_sandboxing=False,  # Disable for faster development
        max_execution_time=120,   # Longer timeout for debugging
        max_memory_usage=2 * 1024 * 1024 * 1024,  # 2GB
        max_cpu_percent=80.0,
        allowed_file_types=['.txt', '.md', '.py', '.json', '.csv', '.xml'],
        blocked_file_types=['.exe', '.bat', '.cmd'],
        max_file_size=50 * 1024 * 1024,  # 50MB
        enable_audit_logging=True
    )

# Production environment - strict security
def configure_prod_security():
    update_security_config(
        enable_sandboxing=True,
        max_execution_time=30,
        max_memory_usage=512 * 1024 * 1024,  # 512MB
        max_cpu_percent=50.0,
        allowed_file_types=['.txt', '.md', '.json', '.csv'],
        blocked_file_types=['.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.jar'],
        max_file_size=10 * 1024 * 1024,  # 10MB
        allowed_domains=['api.example.com', 'data.example.com'],
        blocked_domains=['localhost', '127.0.0.1', '0.0.0.0'],
        max_network_requests=5,
        enable_audit_logging=True
    )
```

## Troubleshooting

### Common Issues

#### Tool Registration Failures

**Problem**: Tool not appearing in available tools list

**Solutions**:
1. Check that the tool class inherits from `CustomToolBase`
2. Verify the `@register_custom_tool` decorator is applied correctly
3. Ensure all required methods (`_get_metadata`, `_execute`) are implemented
4. Check for import errors in the tool module

#### Security Validation Failures

**Problem**: Security violations preventing tool execution

**Solutions**:
1. Check security level configuration
2. Verify file access permissions
3. Review network request restrictions
4. Check resource usage limits

#### Configuration Loading Issues

**Problem**: Configuration not loading or updating

**Solutions**:
1. Verify configuration file permissions
2. Check JSON syntax in configuration files
3. Ensure configuration schema validation passes
4. Review file watcher setup

### Debugging Tools

#### Tool Validation

```python
from src.extensibility import validate_tool_implementation

# Validate tool implementation
issues = validate_tool_implementation(MyCustomTool)
if issues:
    print("Tool validation issues:")
    for issue in issues:
        print(f"  - {issue}")
```

#### Security Monitoring

```python
from src.security import security_manager

# Get security statistics
stats = security_manager.get_security_stats()
print("Security Statistics:")
for key, value in stats.items():
    print(f"  {key}: {value}")

# Get recent security events
from src.security import security_monitor
events = security_monitor.get_events(limit=10)
for event in events:
    print(f"Event: {event['event_type']} at {event['timestamp']}")
```

#### Configuration Debugging

```python
from src.config_manager import config_manager

# Get configuration summary
summary = config_manager.get_configuration_summary()
print("Configuration Summary:")
for key, value in summary.items():
    print(f"  {key}: {value}")

# List configuration backups
backups = config_manager.list_backups()
print("Available Backups:")
for backup in backups:
    print(f"  {backup['file']} - {backup['created_at']}")
```

### Getting Help

If you encounter issues with the extensibility and security features:

1. **Check the logs**: Review application logs for error messages
2. **Validate configurations**: Use the validation tools provided
3. **Test incrementally**: Test components individually before integration
4. **Review examples**: Refer to the provided examples for guidance
5. **Check documentation**: Review this guide and API documentation

For additional support, please refer to the main project documentation or create an issue in the project repository. 