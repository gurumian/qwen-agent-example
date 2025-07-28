"""
Security Module for Qwen-Agent Chatbot

This module provides comprehensive security features including:
- Code execution sandboxing
- File access controls
- Resource monitoring
- Security logging and audit trails

📚 Documentation:
- Security Features: docs/EXTENSIBILITY_GUIDE.md#security-implementation
- Extensibility Guide: docs/EXTENSIBILITY_GUIDE.md
- Configuration: docs/EXTENSIBILITY_GUIDE.md#configuration-management

🔗 Quick Navigation:
- python -m src.doc_cli doc security
- python -m src.doc_cli source security
- python -m src.doc_cli github security
- python -m src.doc_cli search "security"
"""

import os
import sys
import time
import json
import logging
import signal
import threading
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
import traceback
import psutil
import hashlib
import secrets

from pydantic import BaseModel, Field, validator


# Configure logging
logger = logging.getLogger(__name__)


class SecurityViolation(Exception):
    """Raised when a security violation is detected."""
    pass


class ResourceLimitExceeded(Exception):
    """Raised when resource limits are exceeded."""
    pass


class SecurityLevel(str, Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    RESTRICTED = "restricted"


@dataclass
class SecurityConfig:
    """Configuration for security settings."""
    # Code execution settings
    enable_sandboxing: bool = True
    max_execution_time: int = 30  # seconds
    max_memory_usage: int = 512 * 1024 * 1024  # 512MB
    max_cpu_percent: float = 50.0
    
    # File access settings
    allowed_file_types: List[str] = field(default_factory=lambda: [
        '.txt', '.md', '.py', '.json', '.csv', '.xml', '.html', '.css', '.js'
    ])
    blocked_file_types: List[str] = field(default_factory=lambda: [
        '.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.js', '.jar'
    ])
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_directories: List[str] = field(default_factory=lambda: [
        '/tmp', '/var/tmp', './temp_uploads', './workspace'
    ])
    
    # Network settings
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=lambda: [
        'localhost', '127.0.0.1', '0.0.0.0'
    ])
    max_network_requests: int = 10
    
    # Security monitoring
    enable_audit_logging: bool = True
    audit_log_file: str = "security_audit.log"
    max_audit_log_size: int = 100 * 1024 * 1024  # 100MB


class ResourceMonitor:
    """Monitors resource usage during code execution."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
        self.start_cpu = psutil.Process().cpu_percent()
        self.network_requests = 0
        self.file_operations = 0
        
    def check_limits(self) -> bool:
        """Check if resource usage is within limits."""
        current_time = time.time()
        current_memory = psutil.Process().memory_info().rss
        current_cpu = psutil.Process().cpu_percent()
        
        # Check execution time
        if current_time - self.start_time > self.config.max_execution_time:
            raise ResourceLimitExceeded(f"Execution time exceeded {self.config.max_execution_time} seconds")
        
        # Check memory usage
        memory_increase = current_memory - self.start_memory
        if memory_increase > self.config.max_memory_usage:
            raise ResourceLimitExceeded(f"Memory usage exceeded {self.config.max_memory_usage} bytes")
        
        # Check CPU usage
        if current_cpu > self.config.max_cpu_percent:
            raise ResourceLimitExceeded(f"CPU usage exceeded {self.config.max_cpu_percent}%")
        
        # Check network requests
        if self.network_requests > self.config.max_network_requests:
            raise ResourceLimitExceeded(f"Network requests exceeded {self.config.max_network_requests}")
        
        return True
    
    def log_network_request(self):
        """Log a network request."""
        self.network_requests += 1
        self.check_limits()
    
    def log_file_operation(self):
        """Log a file operation."""
        self.file_operations += 1
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current resource usage statistics."""
        current_time = time.time()
        current_memory = psutil.Process().memory_info().rss
        
        return {
            'execution_time': current_time - self.start_time,
            'memory_usage': current_memory - self.start_memory,
            'network_requests': self.network_requests,
            'file_operations': self.file_operations
        }


class CodeSandbox:
    """Provides sandboxed code execution environment."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.monitor = ResourceMonitor(config)
        
        # Restricted modules and functions
        self.blocked_modules = {
            'os', 'sys', 'subprocess', 'multiprocessing', 'threading',
            'socket', 'urllib', 'requests', 'http', 'ftplib', 'smtplib',
            'pickle', 'marshal', 'ctypes', 'mmap', 'signal'
        }
        
        self.blocked_functions = {
            'eval', 'exec', 'compile', 'input', 'raw_input',
            'open', 'file', '__import__', 'reload', 'globals', 'locals'
        }
    
    def validate_code(self, code: str) -> List[str]:
        """Validate code for security violations."""
        violations = []
        
        # Check for blocked modules
        for module in self.blocked_modules:
            if f"import {module}" in code or f"from {module}" in code:
                violations.append(f"Blocked module import: {module}")
        
        # Check for blocked functions
        for func in self.blocked_functions:
            if func in code:
                violations.append(f"Blocked function usage: {func}")
        
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            'subprocess.call', 'subprocess.Popen', 'os.system',
            'eval(', 'exec(', '__import__', 'globals()', 'locals()'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                violations.append(f"Dangerous pattern detected: {pattern}")
        
        return violations
    
    @contextmanager
    def sandboxed_execution(self, code: str, timeout: Optional[int] = None):
        """Execute code in a sandboxed environment."""
        if not self.config.enable_sandboxing:
            yield
            return
        
        # Validate code
        violations = self.validate_code(code)
        if violations:
            raise SecurityViolation(f"Code validation failed: {'; '.join(violations)}")
        
        # Create restricted globals
        restricted_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sum': sum,
                'max': max,
                'min': min,
                'abs': abs,
                'round': round,
                'pow': pow,
                'divmod': divmod,
                'all': all,
                'any': any,
                'sorted': sorted,
                'reversed': reversed,
                'isinstance': isinstance,
                'issubclass': issubclass,
                'hasattr': hasattr,
                'getattr': getattr,
                'setattr': setattr,
                'delattr': delattr,
                'dir': dir,
                'vars': vars,
                'type': type,
                'id': id,
                'hash': hash,
                'repr': repr,
                'ascii': ascii,
                'format': format,
                'bin': bin,
                'oct': oct,
                'hex': hex,
                'chr': chr,
                'ord': ord,
                'bool': bool,
                'complex': complex,
                'bytes': bytes,
                'bytearray': bytearray,
                'memoryview': memoryview,
                'slice': slice,
                'property': property,
                'staticmethod': staticmethod,
                'classmethod': classmethod,
                'super': super,
                'object': object,
                'Exception': Exception,
                'BaseException': BaseException,
                'StopIteration': StopIteration,
                'GeneratorExit': GeneratorExit,
                'ArithmeticError': ArithmeticError,
                'BufferError': BufferError,
                'LookupError': LookupError,
                'AssertionError': AssertionError,
                'AttributeError': AttributeError,
                'EOFError': EOFError,
                'FloatingPointError': FloatingPointError,
                'ImportError': ImportError,
                'ModuleNotFoundError': ModuleNotFoundError,
                'IndexError': IndexError,
                'KeyError': KeyError,
                'KeyboardInterrupt': KeyboardInterrupt,
                'MemoryError': MemoryError,
                'NameError': NameError,
                'NotImplementedError': NotImplementedError,
                'OSError': OSError,
                'OverflowError': OverflowError,
                'RecursionError': RecursionError,
                'ReferenceError': ReferenceError,
                'RuntimeError': RuntimeError,
                'SyntaxError': SyntaxError,
                'SystemError': SystemError,
                'TypeError': TypeError,
                'UnboundLocalError': UnboundLocalError,
                'UnicodeError': UnicodeError,
                'ValueError': ValueError,
                'ZeroDivisionError': ZeroDivisionError,
                'BlockingIOError': BlockingIOError,
                'ChildProcessError': ChildProcessError,
                'ConnectionError': ConnectionError,
                'BrokenPipeError': BrokenPipeError,
                'ConnectionAbortedError': ConnectionAbortedError,
                'ConnectionRefusedError': ConnectionRefusedError,
                'ConnectionResetError': ConnectionResetError,
                'FileExistsError': FileExistsError,
                'FileNotFoundError': FileNotFoundError,
                'InterruptedError': InterruptedError,
                'IsADirectoryError': IsADirectoryError,
                'NotADirectoryError': NotADirectoryError,
                'PermissionError': PermissionError,
                'ProcessLookupError': ProcessLookupError,
                'TimeoutError': TimeoutError,
                'UnicodeDecodeError': UnicodeDecodeError,
                'UnicodeEncodeError': UnicodeEncodeError,
                'UnicodeTranslateError': UnicodeTranslateError,
                'Warning': Warning,
                'UserWarning': UserWarning,
                'DeprecationWarning': DeprecationWarning,
                'PendingDeprecationWarning': PendingDeprecationWarning,
                'SyntaxWarning': SyntaxWarning,
                'RuntimeWarning': RuntimeWarning,
                'FutureWarning': FutureWarning,
                'ImportWarning': ImportWarning,
                'UnicodeWarning': UnicodeWarning,
                'BytesWarning': BytesWarning,
                'ResourceWarning': ResourceWarning,
            }
        }
        
        # Create restricted locals
        restricted_locals = {}
        
        execution_timeout = timeout or self.config.max_execution_time
        
        try:
            # Set up monitoring
            self.monitor = ResourceMonitor(self.config)
            
            # Execute code with timeout
            def execute_with_timeout():
                try:
                    exec(code, restricted_globals, restricted_locals)
                    return restricted_locals
                except Exception as e:
                    raise e
            
            # Use threading for timeout
            result = None
            exception = None
            
            def target():
                nonlocal result, exception
                try:
                    result = execute_with_timeout()
                except Exception as e:
                    exception = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=execution_timeout)
            
            if thread.is_alive():
                raise ResourceLimitExceeded(f"Code execution timed out after {execution_timeout} seconds")
            
            if exception:
                raise exception
            
            yield result
            
        except Exception as e:
            logger.error(f"Sandboxed execution failed: {e}")
            raise
        finally:
            # Log resource usage
            stats = self.monitor.get_usage_stats()
            logger.info(f"Code execution stats: {stats}")


class FileSecurityManager:
    """Manages file access security and validation."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
    
    def validate_file_path(self, file_path: str) -> bool:
        """Validate if a file path is allowed."""
        try:
            path = Path(file_path).resolve()
            
            # Check if path is in allowed directories
            allowed = False
            for allowed_dir in self.config.allowed_directories:
                if str(path).startswith(str(Path(allowed_dir).resolve())):
                    allowed = True
                    break
            
            if not allowed:
                logger.warning(f"File path not in allowed directories: {file_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"File path validation failed: {e}")
            return False
    
    def validate_file_type(self, file_path: str) -> bool:
        """Validate if a file type is allowed."""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            # Check blocked file types
            if file_ext in self.config.blocked_file_types:
                logger.warning(f"Blocked file type: {file_ext}")
                return False
            
            # Check allowed file types
            if self.config.allowed_file_types and file_ext not in self.config.allowed_file_types:
                logger.warning(f"File type not allowed: {file_ext}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"File type validation failed: {e}")
            return False
    
    def validate_file_size(self, file_path: str) -> bool:
        """Validate if a file size is within limits."""
        try:
            if not os.path.exists(file_path):
                return True  # File doesn't exist yet
            
            file_size = os.path.getsize(file_path)
            if file_size > self.config.max_file_size:
                logger.warning(f"File size exceeds limit: {file_size} > {self.config.max_file_size}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"File size validation failed: {e}")
            return False
    
    def validate_file_access(self, file_path: str, operation: str = "read") -> bool:
        """Comprehensive file access validation."""
        if not self.validate_file_path(file_path):
            return False
        
        if not self.validate_file_type(file_path):
            return False
        
        if not self.validate_file_size(file_path):
            return False
        
        return True
    
    def create_safe_temp_file(self, suffix: str = "", prefix: str = "secure_") -> str:
        """Create a safe temporary file."""
        try:
            # Create temp file in allowed directory
            temp_dir = None
            for allowed_dir in self.config.allowed_directories:
                if os.path.exists(allowed_dir) and os.access(allowed_dir, os.W_OK):
                    temp_dir = allowed_dir
                    break
            
            if not temp_dir:
                temp_dir = tempfile.gettempdir()
            
            fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=temp_dir)
            os.close(fd)
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to create safe temp file: {e}")
            raise
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """Clean up temporary files."""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Cleaned up temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {file_path}: {e}")


class NetworkSecurityManager:
    """Manages network access security."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
    
    def validate_url(self, url: str) -> bool:
        """Validate if a URL is allowed."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check blocked domains
            if domain in self.config.blocked_domains:
                logger.warning(f"Blocked domain: {domain}")
                return False
            
            # Check allowed domains
            if self.config.allowed_domains and domain not in self.config.allowed_domains:
                logger.warning(f"Domain not allowed: {domain}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"URL validation failed: {e}")
            return False
    
    def validate_network_request(self, url: str, method: str = "GET") -> bool:
        """Validate network request."""
        if not self.validate_url(url):
            return False
        
        # Additional validation can be added here
        return True


class SecurityAuditLogger:
    """Logs security events for audit purposes."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.log_file = config.audit_log_file
        self.events = []
    
    def log_event(self, event_type: str, details: Dict[str, Any], user_id: Optional[str] = None):
        """Log a security event."""
        if not self.config.enable_audit_logging:
            return
        
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
            logger.error(f"Failed to write to audit log: {e}")
    
    def get_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get security events."""
        events = self.events
        if event_type:
            events = [e for e in events if e['event_type'] == event_type]
        return events[-limit:]
    
    def clear_events(self):
        """Clear stored events."""
        self.events.clear()


class SecurityManager:
    """Main security manager that coordinates all security features."""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.code_sandbox = CodeSandbox(self.config)
        self.file_manager = FileSecurityManager(self.config)
        self.network_manager = NetworkSecurityManager(self.config)
        self.audit_logger = SecurityAuditLogger(self.config)
    
    def execute_code_safely(self, code: str, timeout: Optional[int] = None, user_id: Optional[str] = None):
        """Execute code with security measures."""
        try:
            # Log execution attempt
            self.audit_logger.log_event(
                'code_execution_attempt',
                {'code_length': len(code), 'timeout': timeout},
                user_id
            )
            
            # Execute in sandbox
            with self.code_sandbox.sandboxed_execution(code, timeout) as result:
                # Log successful execution
                self.audit_logger.log_event(
                    'code_execution_success',
                    {'result_type': type(result).__name__},
                    user_id
                )
                return result
                
        except Exception as e:
            # Log execution failure
            self.audit_logger.log_event(
                'code_execution_failure',
                {'error': str(e), 'error_type': type(e).__name__},
                user_id
            )
            raise
    
    def validate_file_operation(self, file_path: str, operation: str, user_id: Optional[str] = None) -> bool:
        """Validate file operation."""
        try:
            # Log file operation attempt
            self.audit_logger.log_event(
                'file_operation_attempt',
                {'file_path': file_path, 'operation': operation},
                user_id
            )
            
            # Validate operation
            if self.file_manager.validate_file_access(file_path, operation):
                # Log successful validation
                self.audit_logger.log_event(
                    'file_operation_success',
                    {'file_path': file_path, 'operation': operation},
                    user_id
                )
                return True
            else:
                # Log failed validation
                self.audit_logger.log_event(
                    'file_operation_failure',
                    {'file_path': file_path, 'operation': operation, 'reason': 'validation_failed'},
                    user_id
                )
                return False
                
        except Exception as e:
            # Log validation error
            self.audit_logger.log_event(
                'file_operation_error',
                {'file_path': file_path, 'operation': operation, 'error': str(e)},
                user_id
            )
            return False
    
    def validate_network_request(self, url: str, method: str = "GET", user_id: Optional[str] = None) -> bool:
        """Validate network request."""
        try:
            # Log network request attempt
            self.audit_logger.log_event(
                'network_request_attempt',
                {'url': url, 'method': method},
                user_id
            )
            
            # Validate request
            if self.network_manager.validate_network_request(url, method):
                # Log successful validation
                self.audit_logger.log_event(
                    'network_request_success',
                    {'url': url, 'method': method},
                    user_id
                )
                return True
            else:
                # Log failed validation
                self.audit_logger.log_event(
                    'network_request_failure',
                    {'url': url, 'method': method, 'reason': 'validation_failed'},
                    user_id
                )
                return False
                
        except Exception as e:
            # Log validation error
            self.audit_logger.log_event(
                'network_request_error',
                {'url': url, 'method': method, 'error': str(e)},
                user_id
            )
            return False
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        events = self.audit_logger.get_events()
        
        stats = {
            'total_events': len(events),
            'code_executions': len([e for e in events if e['event_type'] == 'code_execution_success']),
            'code_failures': len([e for e in events if e['event_type'] == 'code_execution_failure']),
            'file_operations': len([e for e in events if e['event_type'].startswith('file_operation')]),
            'network_requests': len([e for e in events if e['event_type'].startswith('network_request')]),
            'security_violations': len([e for e in events if 'failure' in e['event_type'] or 'error' in e['event_type']])
        }
        
        return stats


# Global security manager instance
security_manager = SecurityManager()


# Security decorators for easy integration
def secure_code_execution(timeout: Optional[int] = None):
    """Decorator for secure code execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            return security_manager.execute_code_safely(
                func(*args, **kwargs), timeout
            )
        return wrapper
    return decorator


def secure_file_operation(operation: str = "read"):
    """Decorator for secure file operations."""
    def decorator(func):
        def wrapper(file_path: str, *args, **kwargs):
            if not security_manager.validate_file_operation(file_path, operation):
                raise SecurityViolation(f"File operation not allowed: {operation} on {file_path}")
            return func(file_path, *args, **kwargs)
        return wrapper
    return decorator


def secure_network_request(method: str = "GET"):
    """Decorator for secure network requests."""
    def decorator(func):
        def wrapper(url: str, *args, **kwargs):
            if not security_manager.validate_network_request(url, method):
                raise SecurityViolation(f"Network request not allowed: {method} to {url}")
            return func(url, *args, **kwargs)
        return wrapper
    return decorator 