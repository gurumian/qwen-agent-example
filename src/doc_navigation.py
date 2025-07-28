"""
Documentation Navigation System for Qwen-Agent Chatbot

This module provides comprehensive documentation navigation features including:
- GitHub repository integration
- Source code location mapping
- Documentation section indexing
- Quick navigation utilities
- Cursor IDE integration
"""

import os
import json
import webbrowser
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DocSection(str, Enum):
    """Documentation sections."""
    OVERVIEW = "overview"
    INSTALLATION = "installation"
    QUICK_START = "quick_start"
    API_REFERENCE = "api_reference"
    EXAMPLES = "examples"
    EXTENSIBILITY = "extensibility"
    SECURITY = "security"
    DEPLOYMENT = "deployment"
    TROUBLESHOOTING = "troubleshooting"
    CONTRIBUTING = "contributing"


class SourceLocation(str, Enum):
    """Source code locations."""
    MAIN_API = "main_api"
    AGENT_MANAGER = "agent_manager"
    TASK_TYPES = "task_types"
    MULTIMODAL = "multimodal"
    WEBUI = "webui"
    CLI = "cli"
    SECURITY = "security"
    EXTENSIBILITY = "extensibility"
    CONFIG_MANAGER = "config_manager"
    MODELS = "models"


@dataclass
class DocLink:
    """Documentation link information."""
    title: str
    description: str
    url: str
    section: DocSection
    source_location: Optional[SourceLocation] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class SourceMapping:
    """Source code mapping information."""
    location: SourceLocation
    file_path: str
    description: str
    github_url: str
    local_path: str
    key_functions: List[str] = field(default_factory=list)
    related_docs: List[DocSection] = field(default_factory=list)


class DocumentationNavigator:
    """Main documentation navigation system."""
    
    def __init__(self, project_root: str = ".", github_repo: str = "QwenLM/Qwen-Agent"):
        self.project_root = Path(project_root)
        self.github_repo = github_repo
        self.github_base_url = f"https://github.com/{github_repo}"
        self.docs_dir = self.project_root / "docs"
        
        # Initialize documentation links
        self.doc_links = self._initialize_doc_links()
        self.source_mappings = self._initialize_source_mappings()
        
        # Create docs directory if it doesn't exist
        self.docs_dir.mkdir(exist_ok=True)
    
    def _initialize_doc_links(self) -> Dict[str, DocLink]:
        """Initialize documentation links."""
        return {
            "overview": DocLink(
                title="Project Overview",
                description="Introduction to the Qwen-Agent Chatbot system",
                url=f"{self.github_base_url}#readme",
                section=DocSection.OVERVIEW,
                tags=["introduction", "overview", "getting-started"]
            ),
            "installation": DocLink(
                title="Installation Guide",
                description="Complete installation and setup instructions",
                url=f"{self.github_base_url}#installation",
                section=DocSection.INSTALLATION,
                source_location=SourceLocation.MAIN_API,
                file_path="INSTALLATION.md",
                tags=["setup", "installation", "dependencies"]
            ),
            "quick_start": DocLink(
                title="Quick Start Guide",
                description="Get up and running quickly with the chatbot",
                url=f"{self.github_base_url}#quick-start",
                section=DocSection.QUICK_START,
                tags=["quick-start", "tutorial", "examples"]
            ),
            "api_reference": DocLink(
                title="API Reference",
                description="Complete API documentation and endpoints",
                url=f"{self.github_base_url}/blob/main/README.md#api-usage",
                section=DocSection.API_REFERENCE,
                source_location=SourceLocation.MAIN_API,
                file_path="src/api.py",
                tags=["api", "endpoints", "reference"]
            ),
            "extensibility": DocLink(
                title="Extensibility Guide",
                description="How to create custom tools and extend the system",
                url="docs/EXTENSIBILITY_GUIDE.md",
                section=DocSection.EXTENSIBILITY,
                source_location=SourceLocation.EXTENSIBILITY,
                file_path="src/extensibility.py",
                tags=["custom-tools", "extensibility", "development"]
            ),
            "security": DocLink(
                title="Security Features",
                description="Security implementation and best practices",
                url="docs/EXTENSIBILITY_GUIDE.md#security-implementation",
                section=DocSection.SECURITY,
                source_location=SourceLocation.SECURITY,
                file_path="src/security.py",
                tags=["security", "sandboxing", "validation"]
            ),
            "deployment": DocLink(
                title="Deployment Guide",
                description="Production deployment and configuration",
                url="INSTALLATION.md#deployment",
                section=DocSection.DEPLOYMENT,
                tags=["deployment", "production", "docker"]
            ),
            "troubleshooting": DocLink(
                title="Troubleshooting",
                description="Common issues and solutions",
                url="docs/EXTENSIBILITY_GUIDE.md#troubleshooting",
                section=DocSection.TROUBLESHOOTING,
                tags=["troubleshooting", "debugging", "issues"]
            ),
            "contributing": DocLink(
                title="Contributing Guide",
                description="How to contribute to the project",
                url=f"{self.github_base_url}/blob/main/CONTRIBUTING.md",
                section=DocSection.CONTRIBUTING,
                tags=["contributing", "development", "community"]
            )
        }
    
    def _initialize_source_mappings(self) -> Dict[SourceLocation, SourceMapping]:
        """Initialize source code mappings."""
        return {
            SourceLocation.MAIN_API: SourceMapping(
                location=SourceLocation.MAIN_API,
                file_path="src/api.py",
                description="Main FastAPI application and endpoints",
                github_url=f"{self.github_base_url}/blob/main/src/api.py",
                local_path="src/api.py",
                key_functions=["chat", "chat_stream", "health", "tasks"],
                related_docs=[DocSection.API_REFERENCE, DocSection.OVERVIEW]
            ),
            SourceLocation.AGENT_MANAGER: SourceMapping(
                location=SourceLocation.AGENT_MANAGER,
                file_path="src/agent_manager.py",
                description="Qwen-Agent instance management and configuration",
                github_url=f"{self.github_base_url}/blob/main/src/agent_manager.py",
                local_path="src/agent_manager.py",
                key_functions=["create_agent", "create_task_agent", "switch_agent_task"],
                related_docs=[DocSection.API_REFERENCE, DocSection.OVERVIEW]
            ),
            SourceLocation.TASK_TYPES: SourceMapping(
                location=SourceLocation.TASK_TYPES,
                file_path="src/task_types.py",
                description="Task segmentation and configuration management",
                github_url=f"{self.github_base_url}/blob/main/src/task_types.py",
                local_path="src/task_types.py",
                key_functions=["TaskManager", "TaskConfiguration", "create_custom_task"],
                related_docs=[DocSection.OVERVIEW, DocSection.EXTENSIBILITY]
            ),
            SourceLocation.MULTIMODAL: SourceMapping(
                location=SourceLocation.MULTIMODAL,
                file_path="src/multimodal.py",
                description="Multi-modal processing and file handling",
                github_url=f"{self.github_base_url}/blob/main/src/multimodal.py",
                local_path="src/multimodal.py",
                key_functions=["process_multimodal_input", "extract_text", "analyze_image"],
                related_docs=[DocSection.API_REFERENCE, DocSection.OVERVIEW]
            ),
            SourceLocation.WEBUI: SourceMapping(
                location=SourceLocation.WEBUI,
                file_path="src/webui.py",
                description="Gradio web interface implementation",
                github_url=f"{self.github_base_url}/blob/main/src/webui.py",
                local_path="src/webui.py",
                key_functions=["create_webui", "WebUI"],
                related_docs=[DocSection.OVERVIEW, DocSection.QUICK_START]
            ),
            SourceLocation.CLI: SourceMapping(
                location=SourceLocation.CLI,
                file_path="src/cli.py",
                description="Command line interface implementation",
                github_url=f"{self.github_base_url}/blob/main/src/cli.py",
                local_path="src/cli.py",
                key_functions=["create_cli", "CLI"],
                related_docs=[DocSection.OVERVIEW, DocSection.QUICK_START]
            ),
            SourceLocation.SECURITY: SourceMapping(
                location=SourceLocation.SECURITY,
                file_path="src/security.py",
                description="Security framework and sandboxing",
                github_url=f"{self.github_base_url}/blob/main/src/security.py",
                local_path="src/security.py",
                key_functions=["SecurityManager", "CodeSandbox", "FileSecurityManager"],
                related_docs=[DocSection.SECURITY, DocSection.EXTENSIBILITY]
            ),
            SourceLocation.EXTENSIBILITY: SourceMapping(
                location=SourceLocation.EXTENSIBILITY,
                file_path="src/extensibility.py",
                description="Custom tool framework and extensibility",
                github_url=f"{self.github_base_url}/blob/main/src/extensibility.py",
                local_path="src/extensibility.py",
                key_functions=["CustomToolBase", "ToolRegistry", "register_custom_tool"],
                related_docs=[DocSection.EXTENSIBILITY, DocSection.SECURITY]
            ),
            SourceLocation.CONFIG_MANAGER: SourceMapping(
                location=SourceLocation.CONFIG_MANAGER,
                file_path="src/config_manager.py",
                description="Configuration management system",
                github_url=f"{self.github_base_url}/blob/main/src/config_manager.py",
                local_path="src/config_manager.py",
                key_functions=["ConfigurationManager", "get_config", "update_config"],
                related_docs=[DocSection.EXTENSIBILITY, DocSection.DEPLOYMENT]
            ),
            SourceLocation.MODELS: SourceMapping(
                location=SourceLocation.MODELS,
                file_path="src/models.py",
                description="Pydantic models and data structures",
                github_url=f"{self.github_base_url}/blob/main/src/models.py",
                local_path="src/models.py",
                key_functions=["ChatRequest", "ChatResponse", "TaskRequest"],
                related_docs=[DocSection.API_REFERENCE, DocSection.OVERVIEW]
            )
        }
    
    def get_doc_link(self, key: str) -> Optional[DocLink]:
        """Get a documentation link by key."""
        return self.doc_links.get(key)
    
    def get_source_mapping(self, location: SourceLocation) -> Optional[SourceMapping]:
        """Get source code mapping by location."""
        return self.source_mappings.get(location)
    
    def list_doc_sections(self) -> List[DocLink]:
        """List all documentation sections."""
        return list(self.doc_links.values())
    
    def list_source_locations(self) -> List[SourceMapping]:
        """List all source code locations."""
        return list(self.source_mappings.values())
    
    def search_docs(self, query: str) -> List[DocLink]:
        """Search documentation by query."""
        query_lower = query.lower()
        results = []
        
        for link in self.doc_links.values():
            if (query_lower in link.title.lower() or 
                query_lower in link.description.lower() or
                any(query_lower in tag.lower() for tag in link.tags)):
                results.append(link)
        
        return results
    
    def search_source(self, query: str) -> List[SourceMapping]:
        """Search source code by query."""
        query_lower = query.lower()
        results = []
        
        for mapping in self.source_mappings.values():
            if (query_lower in mapping.description.lower() or
                query_lower in mapping.file_path.lower() or
                any(query_lower in func.lower() for func in mapping.key_functions)):
                results.append(mapping)
        
        return results
    
    def open_doc_link(self, key: str) -> bool:
        """Open a documentation link in the browser."""
        link = self.get_doc_link(key)
        if not link:
            logger.error(f"Documentation link not found: {key}")
            return False
        
        try:
            webbrowser.open(link.url)
            logger.info(f"Opened documentation: {link.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to open documentation: {e}")
            return False
    
    def open_source_file(self, location: SourceLocation, line_number: Optional[int] = None) -> bool:
        """Open a source file in the default editor."""
        mapping = self.get_source_mapping(location)
        if not mapping:
            logger.error(f"Source mapping not found: {location}")
            return False
        
        file_path = self.project_root / mapping.local_path
        if not file_path.exists():
            logger.error(f"Source file not found: {file_path}")
            return False
        
        try:
            # Try to open with Cursor if available
            if self._open_with_cursor(file_path, line_number):
                return True
            
            # Fallback to default editor
            if os.name == 'nt':  # Windows
                os.startfile(str(file_path))
            elif os.name == 'posix':  # macOS/Linux
                subprocess.run(['xdg-open', str(file_path)], check=True)
            
            logger.info(f"Opened source file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to open source file: {e}")
            return False
    
    def _open_with_cursor(self, file_path: Path, line_number: Optional[int] = None) -> bool:
        """Try to open file with Cursor IDE."""
        try:
            # Check if Cursor is available
            cursor_paths = [
                "/usr/bin/cursor",
                "/usr/local/bin/cursor",
                "/Applications/Cursor.app/Contents/MacOS/Cursor",
                os.path.expanduser("~/AppData/Local/Programs/Cursor/Cursor.exe")
            ]
            
            cursor_path = None
            for path in cursor_paths:
                if os.path.exists(path):
                    cursor_path = path
                    break
            
            if not cursor_path:
                return False
            
            # Build command
            cmd = [cursor_path, str(file_path)]
            if line_number:
                cmd.extend(["--line", str(line_number)])
            
            subprocess.run(cmd, check=True)
            logger.info(f"Opened with Cursor: {file_path}")
            return True
            
        except Exception as e:
            logger.debug(f"Failed to open with Cursor: {e}")
            return False
    
    def open_github_file(self, location: SourceLocation, line_number: Optional[int] = None) -> bool:
        """Open a file on GitHub."""
        mapping = self.get_source_mapping(location)
        if not mapping:
            logger.error(f"Source mapping not found: {location}")
            return False
        
        url = mapping.github_url
        if line_number:
            url += f"#L{line_number}"
        
        try:
            webbrowser.open(url)
            logger.info(f"Opened GitHub file: {mapping.file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to open GitHub file: {e}")
            return False
    
    def generate_doc_index(self) -> Dict[str, Any]:
        """Generate a documentation index."""
        return {
            "project_info": {
                "name": "Qwen-Agent Chatbot",
                "github_repo": self.github_repo,
                "github_url": self.github_base_url,
                "project_root": str(self.project_root)
            },
            "documentation_sections": {
                key: {
                    "title": link.title,
                    "description": link.description,
                    "url": link.url,
                    "section": link.section.value,
                    "tags": link.tags
                }
                for key, link in self.doc_links.items()
            },
            "source_locations": {
                location.value: {
                    "file_path": mapping.file_path,
                    "description": mapping.description,
                    "github_url": mapping.github_url,
                    "key_functions": mapping.key_functions,
                    "related_docs": [doc.value for doc in mapping.related_docs]
                }
                for location, mapping in self.source_mappings.items()
            }
        }
    
    def save_doc_index(self, file_path: str = "docs/documentation_index.json") -> bool:
        """Save documentation index to file."""
        try:
            index = self.generate_doc_index()
            file_path = self.project_root / file_path
            file_path.parent.mkdir(exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(index, f, indent=2)
            
            logger.info(f"Saved documentation index: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save documentation index: {e}")
            return False
    
    def create_navigation_commands(self) -> Dict[str, str]:
        """Create navigation commands for Cursor IDE."""
        commands = {}
        
        # Documentation commands
        for key, link in self.doc_links.items():
            commands[f"open_doc_{key}"] = f"Open {link.title}"
        
        # Source file commands
        for location, mapping in self.source_mappings.items():
            commands[f"open_source_{location.value}"] = f"Open {mapping.description}"
            commands[f"open_github_{location.value}"] = f"Open {mapping.file_path} on GitHub"
        
        return commands


class CursorIntegration:
    """Cursor IDE integration utilities."""
    
    def __init__(self, navigator: DocumentationNavigator):
        self.navigator = navigator
    
    def create_cursor_config(self) -> Dict[str, Any]:
        """Create Cursor IDE configuration."""
        return {
            "version": "1.0.0",
            "name": "Qwen-Agent Chatbot Navigation",
            "description": "Navigation commands for Qwen-Agent Chatbot development",
            "commands": self.navigator.create_navigation_commands(),
            "keybindings": {
                "ctrl+shift+d": "open_doc_overview",
                "ctrl+shift+i": "open_doc_installation",
                "ctrl+shift+q": "open_doc_quick_start",
                "ctrl+shift+a": "open_doc_api_reference",
                "ctrl+shift+e": "open_doc_extensibility",
                "ctrl+shift+s": "open_doc_security",
                "ctrl+shift+p": "open_doc_deployment",
                "ctrl+shift+t": "open_doc_troubleshooting"
            },
            "contextMenu": {
                "sourceFiles": [
                    {
                        "label": "Open in Cursor",
                        "command": "open_source_file"
                    },
                    {
                        "label": "Open on GitHub",
                        "command": "open_github_file"
                    }
                ]
            }
        }
    
    def save_cursor_config(self, file_path: str = ".cursor/navigation.json") -> bool:
        """Save Cursor configuration to file."""
        try:
            config = self.create_cursor_config()
            file_path = Path(file_path)
            file_path.parent.mkdir(exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved Cursor configuration: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save Cursor configuration: {e}")
            return False


# Global navigator instance
doc_navigator = DocumentationNavigator()


# Utility functions
def open_documentation(section: str) -> bool:
    """Open documentation section."""
    return doc_navigator.open_doc_link(section)


def open_source_file(location: SourceLocation, line_number: Optional[int] = None) -> bool:
    """Open source file in editor."""
    return doc_navigator.open_source_file(location, line_number)


def open_github_file(location: SourceLocation, line_number: Optional[int] = None) -> bool:
    """Open file on GitHub."""
    return doc_navigator.open_github_file(location, line_number)


def search_documentation(query: str) -> List[DocLink]:
    """Search documentation."""
    return doc_navigator.search_docs(query)


def search_source_code(query: str) -> List[SourceMapping]:
    """Search source code."""
    return doc_navigator.search_source(query)


def generate_documentation_index() -> bool:
    """Generate and save documentation index."""
    return doc_navigator.save_doc_index()


def setup_cursor_integration() -> bool:
    """Setup Cursor IDE integration."""
    cursor_integration = CursorIntegration(doc_navigator)
    return cursor_integration.save_cursor_config() 