# 📚 Documentation Navigation Guide

This guide explains how to use the comprehensive documentation navigation system for the Qwen-Agent Chatbot project.

## 🚀 Quick Start

The documentation navigation system provides quick access to:
- **Documentation sections** (README, guides, API docs)
- **Source code files** (open in your editor)
- **GitHub repository links** (browse online)
- **Search functionality** (find content quickly)

### Basic Commands

```bash
# Quick help
python -m src.doc_cli --help

# List all available options
python -m src.doc_cli list all

# Open documentation
python -m src.doc_cli doc overview

# Open source files
python -m src.doc_cli source main_api

# Search for content
python -m src.doc_cli search "custom tools"
```

## 📖 Documentation Navigation

### Available Documentation Sections

| Section | Description | Command |
|---------|-------------|---------|
| `overview` | Project overview and introduction | `python -m src.doc_cli doc overview` |
| `installation` | Installation and setup guide | `python -m src.doc_cli doc installation` |
| `quick_start` | Quick start tutorial | `python -m src.doc_cli doc quick_start` |
| `api_reference` | Complete API documentation | `python -m src.doc_cli doc api_reference` |
| `extensibility` | Custom tools and extensibility guide | `python -m src.doc_cli doc extensibility` |
| `security` | Security features and implementation | `python -m src.doc_cli doc security` |
| `deployment` | Production deployment guide | `python -m src.doc_cli doc deployment` |
| `troubleshooting` | Common issues and solutions | `python -m src.doc_cli doc troubleshooting` |
| `contributing` | How to contribute to the project | `python -m src.doc_cli doc contributing` |

### Opening Documentation

```bash
# Open any documentation section
python -m src.doc_cli doc <section_name>

# Examples
python -m src.doc_cli doc overview
python -m src.doc_cli doc api_reference
python -m src.doc_cli doc extensibility
```

## 💻 Source Code Navigation

### Available Source Locations

| Location | File | Description | Command |
|----------|------|-------------|---------|
| `main_api` | `src/api.py` | Main FastAPI application | `python -m src.doc_cli source main_api` |
| `agent_manager` | `src/agent_manager.py` | Agent management | `python -m src.doc_cli source agent_manager` |
| `task_types` | `src/task_types.py` | Task configuration | `python -m src.doc_cli source task_types` |
| `multimodal` | `src/multimodal.py` | Multi-modal processing | `python -m src.doc_cli source multimodal` |
| `webui` | `src/webui.py` | Gradio web interface | `python -m src.doc_cli source webui` |
| `cli` | `src/cli.py` | Command line interface | `python -m src.doc_cli source cli` |
| `security` | `src/security.py` | Security framework | `python -m src.doc_cli source security` |
| `extensibility` | `src/extensibility.py` | Custom tool framework | `python -m src.doc_cli source extensibility` |
| `config_manager` | `src/config_manager.py` | Configuration management | `python -m src.doc_cli source config_manager` |
| `models` | `src/models.py` | Pydantic models | `python -m src.doc_cli source models` |

### Opening Source Files

```bash
# Open source file in your default editor
python -m src.doc_cli source <location>

# Jump to specific line number
python -m src.doc_cli source <location> --line <line_number>

# Examples
python -m src.doc_cli source main_api
python -m src.doc_cli source security --line 50
python -m src.doc_cli source extensibility
```

### Opening Files on GitHub

```bash
# Open file on GitHub
python -m src.doc_cli github <location>

# Jump to specific line on GitHub
python -m src.doc_cli github <location> --line <line_number>

# Examples
python -m src.doc_cli github main_api
python -m src.doc_cli github security --line 100
```

## 🔍 Search Functionality

### Search Documentation and Source Code

```bash
# Search everything
python -m src.doc_cli search "query"

# Search only documentation
python -m src.doc_cli search "query" --type docs

# Search only source code
python -m src.doc_cli search "query" --type source

# Examples
python -m src.doc_cli search "custom tools"
python -m src.doc_cli search "security" --type docs
python -m src.doc_cli search "api" --type source
```

### Search Examples

| Query | Description | Results |
|-------|-------------|---------|
| `"custom tools"` | Find custom tool documentation | Extensibility guide, tool examples |
| `"security"` | Find security-related content | Security features, validation, sandboxing |
| `"api"` | Find API-related content | API endpoints, models, documentation |
| `"configuration"` | Find configuration content | Config management, settings, environment |
| `"deployment"` | Find deployment content | Docker, production setup, installation |

## 🛠️ Setup and Utilities

### Generate Documentation Index

```bash
# Generate documentation index
python -m src.doc_cli setup index

# This creates docs/documentation_index.json with:
# - Project information
# - Documentation sections
# - Source code mappings
# - GitHub links
```

### Setup Cursor IDE Integration

```bash
# Setup Cursor IDE integration
python -m src.doc_cli setup cursor

# This creates .cursor/navigation.json with:
# - Navigation commands
# - Keyboard shortcuts
# - Context menu options
```

## ⌨️ Cursor IDE Integration

### Keyboard Shortcuts

When Cursor integration is set up, you can use these shortcuts:

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+D` | Open project overview |
| `Ctrl+Shift+I` | Open installation guide |
| `Ctrl+Shift+Q` | Open quick start guide |
| `Ctrl+Shift+A` | Open API reference |
| `Ctrl+Shift+E` | Open extensibility guide |
| `Ctrl+Shift+S` | Open security guide |
| `Ctrl+Shift+P` | Open deployment guide |
| `Ctrl+Shift+T` | Open troubleshooting guide |

### Context Menu

Right-click on source files to access:
- **Open in Cursor** - Open file in editor
- **Open on GitHub** - Open file on GitHub

## 📁 File Structure

```
docs/
├── EXTENSIBILITY_GUIDE.md      # Custom tools and security
├── NAVIGATION_GUIDE.md         # This guide
└── documentation_index.json    # Auto-generated index

.cursor/
└── navigation.json             # Cursor IDE configuration

src/
├── doc_navigation.py           # Navigation system core
├── doc_cli.py                  # Command-line interface
└── ...                         # Other source files
```

## 🔧 Advanced Usage

### Programmatic Access

You can also use the navigation system programmatically:

```python
from src.doc_navigation import (
    open_documentation,
    open_source_file,
    search_documentation,
    SourceLocation
)

# Open documentation
open_documentation("overview")

# Open source file
open_source_file(SourceLocation.MAIN_API, line_number=50)

# Search documentation
results = search_documentation("custom tools")
```

### Custom Navigation

Extend the navigation system by modifying `src/doc_navigation.py`:

```python
# Add new documentation sections
doc_links["new_section"] = DocLink(
    title="New Section",
    description="Description of new section",
    url="path/to/section",
    section=DocSection.CUSTOM
)

# Add new source locations
source_mappings[SourceLocation.NEW_MODULE] = SourceMapping(
    location=SourceLocation.NEW_MODULE,
    file_path="src/new_module.py",
    description="New module description",
    github_url="https://github.com/...",
    local_path="src/new_module.py"
)
```

## 🐛 Troubleshooting

### Common Issues

**Command not found:**
```bash
# Make sure you're in the project root
cd /path/to/qwen-agent-example

# Check if the module exists
ls src/doc_cli.py
```

**File not opening:**
```bash
# Check if the file exists
ls src/api.py

# Try opening with specific editor
EDITOR=code python -m src.doc_cli source main_api
```

**GitHub links not working:**
```bash
# Check internet connection
curl -I https://github.com

# Verify repository URL in doc_navigation.py
```

### Getting Help

```bash
# Show all available commands
python -m src.doc_cli --help

# Show help for specific command
python -m src.doc_cli doc --help
python -m src.doc_cli source --help
python -m src.doc_cli search --help

# List all available options
python -m src.doc_cli list all
```

## 📚 Related Documentation

- **[Extensibility Guide](EXTENSIBILITY_GUIDE.md)** - Custom tools and security features
- **[README.md](../README.md)** - Project overview and quick start
- **[INSTALLATION.md](../INSTALLATION.md)** - Detailed installation instructions

## 🔗 Quick Reference

### Most Used Commands

```bash
# Quick navigation
python -m src.doc_cli doc overview          # Project overview
python -m src.doc_cli doc api_reference     # API documentation
python -m src.doc_cli doc extensibility     # Custom tools guide

# Source code
python -m src.doc_cli source main_api       # Main API file
python -m src.doc_cli source security       # Security module
python -m src.doc_cli source extensibility  # Extensibility module

# Search
python -m src.doc_cli search "custom tools" # Find custom tool info
python -m src.doc_cli search "security"     # Find security info

# Setup
python -m src.doc_cli setup cursor          # Setup Cursor integration
python -m src.doc_cli setup index           # Generate documentation index
```

This navigation system makes it easy to explore and understand the Qwen-Agent Chatbot project quickly and efficiently! 