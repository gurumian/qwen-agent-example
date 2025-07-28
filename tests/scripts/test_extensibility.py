"""
Test suite for extensibility framework

Tests the custom tool interface, security validation, and tool registration system.
"""

import sys
import os
import time
import json
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.extensibility import (
    CustomToolBase, ToolRegistry, register_custom_tool,
    SecurityLevel, ToolCategory, ToolMetadata, ToolConfiguration,
    SecurityContext, SecurityValidator, TextProcessorTool,
    ConfigurationManager, SecurityMonitor
)
from src.security import SecurityManager, SecurityConfig


def test_tool_metadata():
    """Test tool metadata creation and validation."""
    print("🧪 Testing tool metadata...")
    
    metadata = ToolMetadata(
        name="test_tool",
        description="A test tool for validation",
        category=ToolCategory.UTILITY,
        security_level=SecurityLevel.LOW,
        version="1.0.0",
        author="Test Author",
        tags=["test", "utility"],
        dependencies=["requests"]
    )
    
    assert metadata.name == "test_tool"
    assert metadata.category == ToolCategory.UTILITY
    assert metadata.security_level == SecurityLevel.LOW
    assert "test" in metadata.tags
    
    print("✅ Tool metadata test passed")


def test_tool_configuration():
    """Test tool configuration validation."""
    print("🧪 Testing tool configuration...")
    
    config = ToolConfiguration(
        enabled=True,
        timeout=30,
        max_retries=3,
        security_level=SecurityLevel.MEDIUM,
        allowed_domains=["example.com"],
        blocked_domains=["malicious.com"],
        max_file_size=1024 * 1024,
        allowed_file_types=[".txt", ".md"],
        blocked_file_types=[".exe", ".bat"]
    )
    
    assert config.enabled is True
    assert config.timeout == 30
    assert config.max_retries == 3
    assert config.security_level == SecurityLevel.MEDIUM
    assert "example.com" in config.allowed_domains
    assert "malicious.com" in config.blocked_domains
    
    print("✅ Tool configuration test passed")


def test_security_context():
    """Test security context tracking."""
    print("🧪 Testing security context...")
    
    context = SecurityContext(user_id="test_user", session_id="test_session")
    
    # Log some operations
    context.log_operation("file_read", {"file_path": "/tmp/test.txt"})
    context.log_operation("network_request", {"url": "https://api.example.com"})
    
    assert len(context.operations) == 2
    assert context.operations[0]["operation"] == "file_read"
    assert context.operations[1]["operation"] == "network_request"
    
    execution_time = context.get_execution_time()
    assert execution_time > 0
    
    print("✅ Security context test passed")


def test_security_validator():
    """Test security validation functionality."""
    print("🧪 Testing security validator...")
    
    config = ToolConfiguration(
        allowed_domains=["example.com", "api.github.com"],
        blocked_domains=["malicious.com"],
        allowed_file_types=[".txt", ".md", ".py"],
        blocked_file_types=[".exe", ".bat"],
        max_file_size=1024 * 1024
    )
    
    validator = SecurityValidator(config)
    
    # Test file access validation
    assert validator.validate_file_access("/tmp/test.txt", "read") is True
    assert validator.validate_file_access("/tmp/test.exe", "read") is False
    
    # Test network request validation
    assert validator.validate_network_request("https://api.github.com") is True
    assert validator.validate_network_request("https://malicious.com") is False
    
    print("✅ Security validator test passed")


def test_custom_tool_base():
    """Test custom tool base class functionality."""
    print("🧪 Testing custom tool base class...")
    
    class TestTool(CustomToolBase):
        def _get_metadata(self) -> ToolMetadata:
            return ToolMetadata(
                name="test_tool",
                description="A test tool",
                category=ToolCategory.UTILITY,
                security_level=SecurityLevel.LOW
            )
        
        def _execute(self, params: str, security_context: SecurityContext, **kwargs) -> str:
            return f"Processed: {params}"
    
    tool = TestTool()
    metadata = tool._get_metadata()
    
    assert metadata.name == "test_tool"
    assert metadata.category == ToolCategory.UTILITY
    
    # Test execution with security context
    context = SecurityContext()
    result = tool._execute("test input", context)
    assert result == "Processed: test input"
    
    print("✅ Custom tool base test passed")


def test_tool_registry():
    """Test tool registry functionality."""
    print("🧪 Testing tool registry...")
    
    registry = ToolRegistry()
    
    # Create a test tool
    class TestTool(CustomToolBase):
        def _get_metadata(self) -> ToolMetadata:
            return ToolMetadata(
                name="test_tool",
                description="A test tool",
                category=ToolCategory.UTILITY,
                security_level=SecurityLevel.LOW
            )
        
        def _execute(self, params: str, security_context: SecurityContext, **kwargs) -> str:
            return f"Processed: {params}"
    
    tool = TestTool()
    
    # Test registration
    assert registry.register_tool(tool) is True
    assert "test_tool" in registry.list_tools()
    
    # Test retrieval
    retrieved_tool = registry.get_tool("test_tool")
    assert retrieved_tool is not None
    
    # Test metadata retrieval
    metadata = registry.get_metadata("test_tool")
    assert metadata.name == "test_tool"
    
    # Test filtering by category
    utility_tools = registry.list_tools(ToolCategory.UTILITY)
    assert "test_tool" in utility_tools
    
    # Test filtering by security level
    low_security_tools = registry.get_tools_by_security_level(SecurityLevel.LOW)
    assert "test_tool" in low_security_tools
    
    # Test unregistration
    assert registry.unregister_tool("test_tool") is True
    assert "test_tool" not in registry.list_tools()
    
    print("✅ Tool registry test passed")


def test_text_processor_tool():
    """Test the built-in text processor tool."""
    print("🧪 Testing text processor tool...")
    
    tool = TextProcessorTool()
    metadata = tool._get_metadata()
    
    assert metadata.name == "text_processor"
    assert metadata.category == ToolCategory.DATA_PROCESSING
    assert metadata.security_level == SecurityLevel.LOW
    
    # Test execution
    context = SecurityContext()
    result = tool._execute("Hello, world!", context)
    
    assert "Hello" in result
    assert "world" in result
    
    print("✅ Text processor tool test passed")


def test_tool_decorator():
    """Test the tool registration decorator."""
    print("🧪 Testing tool registration decorator...")
    
    @register_custom_tool(
        name="decorated_tool",
        description="A tool created with decorator",
        category=ToolCategory.UTILITY,
        security_level=SecurityLevel.MEDIUM
    )
    class DecoratedTool(CustomToolBase):
        def _get_metadata(self) -> ToolMetadata:
            return ToolMetadata(
                name="decorated_tool",
                description="A tool created with decorator",
                category=ToolCategory.UTILITY,
                security_level=SecurityLevel.MEDIUM
            )
        
        def _execute(self, params: str, security_context: SecurityContext, **kwargs) -> str:
            return f"Decorated tool processed: {params}"
    
    # The tool should be automatically registered
    registry = ToolRegistry()
    assert "decorated_tool" in registry.list_tools()
    
    tool = registry.get_tool("decorated_tool")
    assert tool is not None
    
    context = SecurityContext()
    result = tool._execute("test input", context)
    assert "Decorated tool processed: test input" in result
    
    print("✅ Tool decorator test passed")


def test_configuration_manager():
    """Test configuration management system."""
    print("🧪 Testing configuration manager...")
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_data = {
            "test_tool": {
                "enabled": True,
                "timeout": 30,
                "security_level": "medium"
            }
        }
        json.dump(config_data, f)
        config_file = f.name
    
    try:
        manager = ConfigurationManager(config_file)
        
        # Test loading configurations
        manager.load_configurations()
        
        # Test getting configuration
        config = manager.get_configuration("test_tool")
        assert config is not None
        assert config.enabled is True
        assert config.timeout == 30
        
        # Test updating configuration
        manager.update_configuration("test_tool", timeout=60)
        updated_config = manager.get_configuration("test_tool")
        assert updated_config.timeout == 60
        
        # Test saving configurations
        assert manager.save_configurations() is True
        
    finally:
        # Cleanup
        os.unlink(config_file)
    
    print("✅ Configuration manager test passed")


def test_security_monitor():
    """Test security monitoring system."""
    print("🧪 Testing security monitor...")
    
    # Create temporary log file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_file = f.name
    
    try:
        monitor = SecurityMonitor(log_file)
        
        # Test logging events
        monitor.log_event("file_access", {
            "file_path": "/tmp/test.txt",
            "operation": "read",
            "user_id": "test_user"
        })
        
        monitor.log_event("network_request", {
            "url": "https://api.example.com",
            "method": "GET",
            "user_id": "test_user"
        })
        
        # Test retrieving events
        events = monitor.get_events()
        assert len(events) >= 2
        
        file_events = monitor.get_events("file_access")
        assert len(file_events) >= 1
        assert file_events[0]["event_type"] == "file_access"
        
        # Test clearing events
        monitor.clear_events()
        events_after_clear = monitor.get_events()
        assert len(events_after_clear) == 0
        
    finally:
        # Cleanup
        if os.path.exists(log_file):
            os.unlink(log_file)
    
    print("✅ Security monitor test passed")


def test_integration_with_security_manager():
    """Test integration between extensibility and security frameworks."""
    print("🧪 Testing extensibility-security integration...")
    
    # Create security manager
    security_config = SecurityConfig()
    security_manager = SecurityManager(security_config)
    
    # Create a tool that uses security features
    class SecureTool(CustomToolBase):
        def _get_metadata(self) -> ToolMetadata:
            return ToolMetadata(
                name="secure_tool",
                description="A tool with security features",
                category=ToolCategory.UTILITY,
                security_level=SecurityLevel.HIGH
            )
        
        def _execute(self, params: str, security_context: SecurityContext, **kwargs) -> str:
            # Test file operation validation
            if "file" in params:
                file_path = "/tmp/test.txt"
                if security_manager.validate_file_operation(file_path, "read"):
                    return f"File access allowed: {file_path}"
                else:
                    return "File access denied"
            
            # Test network request validation
            if "network" in params:
                url = "https://api.example.com"
                if security_manager.validate_network_request(url):
                    return f"Network request allowed: {url}"
                else:
                    return "Network request denied"
            
            return f"Secure processing: {params}"
    
    tool = SecureTool()
    context = SecurityContext()
    
    # Test file operation
    result = tool._execute("file operation", context)
    assert "File access" in result
    
    # Test network operation
    result = tool._execute("network operation", context)
    assert "Network request" in result
    
    print("✅ Extensibility-security integration test passed")


def run_all_tests():
    """Run all extensibility tests."""
    print("🚀 Starting Extensibility Framework Tests")
    print("=" * 50)
    
    test_functions = [
        test_tool_metadata,
        test_tool_configuration,
        test_security_context,
        test_security_validator,
        test_custom_tool_base,
        test_tool_registry,
        test_text_processor_tool,
        test_tool_decorator,
        test_configuration_manager,
        test_security_monitor,
        test_integration_with_security_manager
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All extensibility tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests()) 