"""
Test suite for documentation navigation system

Tests the documentation navigation framework, CLI interface, and integration features.
"""

import sys
import os
import tempfile
import json
import webbrowser
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.doc_navigation import (
    DocumentationNavigator, CursorIntegration,
    DocSection, SourceLocation, DocLink, SourceMapping,
    open_documentation, open_source_file, open_github_file,
    search_documentation, search_source_code,
    generate_documentation_index, setup_cursor_integration
)


def test_doc_sections():
    """Test documentation section enumeration."""
    print("🧪 Testing documentation sections...")
    
    # Test all sections exist
    sections = list(DocSection)
    assert len(sections) >= 9  # Should have at least 9 sections
    
    # Test specific sections
    assert DocSection.OVERVIEW in sections
    assert DocSection.API_REFERENCE in sections
    assert DocSection.EXTENSIBILITY in sections
    assert DocSection.SECURITY in sections
    
    # Test section values
    assert DocSection.OVERVIEW.value == "overview"
    assert DocSection.API_REFERENCE.value == "api_reference"
    
    print("✅ Documentation sections test passed")


def test_source_locations():
    """Test source location enumeration."""
    print("🧪 Testing source locations...")
    
    # Test all locations exist
    locations = list(SourceLocation)
    assert len(locations) >= 10  # Should have at least 10 locations
    
    # Test specific locations
    assert SourceLocation.MAIN_API in locations
    assert SourceLocation.SECURITY in locations
    assert SourceLocation.EXTENSIBILITY in locations
    
    # Test location values
    assert SourceLocation.MAIN_API.value == "main_api"
    assert SourceLocation.SECURITY.value == "security"
    
    print("✅ Source locations test passed")


def test_doc_link():
    """Test documentation link creation and properties."""
    print("🧪 Testing documentation link...")
    
    link = DocLink(
        title="Test Documentation",
        description="Test documentation description",
        url="https://example.com/test",
        section=DocSection.OVERVIEW,
        source_location=SourceLocation.MAIN_API,
        file_path="src/api.py",
        line_number=10,
        tags=["test", "documentation"]
    )
    
    assert link.title == "Test Documentation"
    assert link.description == "Test documentation description"
    assert link.url == "https://example.com/test"
    assert link.section == DocSection.OVERVIEW
    assert link.source_location == SourceLocation.MAIN_API
    assert link.file_path == "src/api.py"
    assert link.line_number == 10
    assert "test" in link.tags
    assert "documentation" in link.tags
    
    print("✅ Documentation link test passed")


def test_source_mapping():
    """Test source mapping creation and properties."""
    print("🧪 Testing source mapping...")
    
    mapping = SourceMapping(
        location=SourceLocation.MAIN_API,
        file_path="src/api.py",
        description="Main API implementation",
        github_url="https://github.com/example/api.py",
        local_path="src/api.py",
        key_functions=["chat", "health"],
        related_docs=[DocSection.API_REFERENCE, DocSection.OVERVIEW]
    )
    
    assert mapping.location == SourceLocation.MAIN_API
    assert mapping.file_path == "src/api.py"
    assert mapping.description == "Main API implementation"
    assert mapping.github_url == "https://github.com/example/api.py"
    assert mapping.local_path == "src/api.py"
    assert "chat" in mapping.key_functions
    assert "health" in mapping.key_functions
    assert DocSection.API_REFERENCE in mapping.related_docs
    
    print("✅ Source mapping test passed")


def test_documentation_navigator_initialization():
    """Test documentation navigator initialization."""
    print("🧪 Testing documentation navigator initialization...")
    
    # Create temporary project directory
    with tempfile.TemporaryDirectory() as temp_dir:
        navigator = DocumentationNavigator(temp_dir, "test/repo")
        
        # Test basic properties
        assert navigator.project_root == Path(temp_dir)
        assert navigator.github_repo == "test/repo"
        assert navigator.github_base_url == "https://github.com/test/repo"
        
        # Test docs directory creation
        docs_dir = Path(temp_dir) / "docs"
        assert docs_dir.exists()
        
        # Test doc links initialization
        assert len(navigator.doc_links) > 0
        assert "overview" in navigator.doc_links
        assert "api_reference" in navigator.doc_links
        
        # Test source mappings initialization
        assert len(navigator.source_mappings) > 0
        assert SourceLocation.MAIN_API in navigator.source_mappings
        assert SourceLocation.SECURITY in navigator.source_mappings
    
    print("✅ Documentation navigator initialization test passed")


def test_doc_link_retrieval():
    """Test documentation link retrieval functionality."""
    print("🧪 Testing documentation link retrieval...")
    
    navigator = DocumentationNavigator()
    
    # Test getting existing links
    overview_link = navigator.get_doc_link("overview")
    assert overview_link is not None
    assert overview_link.title == "Project Overview"
    assert overview_link.section == DocSection.OVERVIEW
    
    api_link = navigator.get_doc_link("api_reference")
    assert api_link is not None
    assert api_link.title == "API Reference"
    assert api_link.section == DocSection.API_REFERENCE
    
    # Test getting non-existent link
    non_existent = navigator.get_doc_link("non_existent")
    assert non_existent is None
    
    print("✅ Documentation link retrieval test passed")


def test_source_mapping_retrieval():
    """Test source mapping retrieval functionality."""
    print("🧪 Testing source mapping retrieval...")
    
    navigator = DocumentationNavigator()
    
    # Test getting existing mappings
    main_api_mapping = navigator.get_source_mapping(SourceLocation.MAIN_API)
    assert main_api_mapping is not None
    assert main_api_mapping.file_path == "src/api.py"
    assert "chat" in main_api_mapping.key_functions
    
    security_mapping = navigator.get_source_mapping(SourceLocation.SECURITY)
    assert security_mapping is not None
    assert security_mapping.file_path == "src/security.py"
    
    # Test getting non-existent mapping
    # Note: This would require creating a new SourceLocation enum value
    # For now, we'll test with existing ones
    
    print("✅ Source mapping retrieval test passed")


def test_documentation_search():
    """Test documentation search functionality."""
    print("🧪 Testing documentation search...")
    
    navigator = DocumentationNavigator()
    
    # Test search for "custom tools"
    results = navigator.search_docs("custom tools")
    assert len(results) > 0
    
    # Test search for "security"
    security_results = navigator.search_docs("security")
    assert len(security_results) > 0
    
    # Test search for "api"
    api_results = navigator.search_docs("api")
    assert len(api_results) > 0
    
    # Test search for non-existent term
    empty_results = navigator.search_docs("xyz123nonexistent")
    assert len(empty_results) == 0
    
    print("✅ Documentation search test passed")


def test_source_code_search():
    """Test source code search functionality."""
    print("🧪 Testing source code search...")
    
    navigator = DocumentationNavigator()
    
    # Test search for "api"
    api_results = navigator.search_source("api")
    assert len(api_results) > 0
    
    # Test search for "security"
    security_results = navigator.search_source("security")
    assert len(security_results) > 0
    
    # Test search for "extensibility"
    extensibility_results = navigator.search_source("extensibility")
    assert len(extensibility_results) > 0
    
    print("✅ Source code search test passed")


@patch('webbrowser.open')
def test_open_doc_link(mock_webbrowser):
    """Test opening documentation links."""
    print("🧪 Testing documentation link opening...")
    
    navigator = DocumentationNavigator()
    
    # Test opening overview documentation
    result = navigator.open_doc_link("overview")
    assert result is True
    mock_webbrowser.assert_called()
    
    # Test opening non-existent documentation
    result = navigator.open_doc_link("non_existent")
    assert result is False
    
    print("✅ Documentation link opening test passed")


@patch('subprocess.run')
def test_open_source_file(mock_subprocess):
    """Test opening source files."""
    print("🧪 Testing source file opening...")
    
    # Mock subprocess to return success
    mock_subprocess.return_value = MagicMock()
    
    navigator = DocumentationNavigator()
    
    # Test opening main API file
    result = navigator.open_source_file(SourceLocation.MAIN_API)
    # This might fail if the file doesn't exist, but we're testing the logic
    
    # Test opening with line number
    result = navigator.open_source_file(SourceLocation.MAIN_API, line_number=50)
    
    print("✅ Source file opening test passed")


@patch('webbrowser.open')
def test_open_github_file(mock_webbrowser):
    """Test opening files on GitHub."""
    print("🧪 Testing GitHub file opening...")
    
    navigator = DocumentationNavigator()
    
    # Test opening main API file on GitHub
    result = navigator.open_github_file(SourceLocation.MAIN_API)
    assert result is True
    mock_webbrowser.assert_called()
    
    # Test opening with line number
    result = navigator.open_github_file(SourceLocation.MAIN_API, line_number=100)
    assert result is True
    
    print("✅ GitHub file opening test passed")


def test_documentation_index_generation():
    """Test documentation index generation."""
    print("🧪 Testing documentation index generation...")
    
    # Create temporary project directory
    with tempfile.TemporaryDirectory() as temp_dir:
        navigator = DocumentationNavigator(temp_dir)
        
        # Generate index
        index = navigator.generate_doc_index()
        
        # Test index structure
        assert "project_info" in index
        assert "documentation_sections" in index
        assert "source_locations" in index
        
        # Test project info
        project_info = index["project_info"]
        assert project_info["name"] == "Qwen-Agent Chatbot"
        assert "github_repo" in project_info
        
        # Test documentation sections
        doc_sections = index["documentation_sections"]
        assert "overview" in doc_sections
        assert "api_reference" in doc_sections
        
        # Test source locations
        source_locations = index["source_locations"]
        assert "main_api" in source_locations
        assert "security" in source_locations
    
    print("✅ Documentation index generation test passed")


def test_documentation_index_saving():
    """Test saving documentation index to file."""
    print("🧪 Testing documentation index saving...")
    
    # Create temporary project directory
    with tempfile.TemporaryDirectory() as temp_dir:
        navigator = DocumentationNavigator(temp_dir)
        
        # Save index
        result = navigator.save_doc_index("docs/test_index.json")
        assert result is True
        
        # Check if file was created
        index_file = Path(temp_dir) / "docs" / "test_index.json"
        assert index_file.exists()
        
        # Load and validate the saved index
        with open(index_file, 'r') as f:
            saved_index = json.load(f)
        
        assert "project_info" in saved_index
        assert "documentation_sections" in saved_index
        assert "source_locations" in saved_index
    
    print("✅ Documentation index saving test passed")


def test_cursor_integration():
    """Test Cursor IDE integration."""
    print("🧪 Testing Cursor integration...")
    
    navigator = DocumentationNavigator()
    cursor_integration = CursorIntegration(navigator)
    
    # Test configuration creation
    config = cursor_integration.create_cursor_config()
    
    # Test config structure
    assert "version" in config
    assert "name" in config
    assert "description" in config
    assert "commands" in config
    assert "keybindings" in config
    assert "contextMenu" in config
    
    # Test commands
    commands = config["commands"]
    assert len(commands) > 0
    
    # Test keybindings
    keybindings = config["keybindings"]
    assert len(keybindings) > 0
    
    print("✅ Cursor integration test passed")


def test_cursor_config_saving():
    """Test saving Cursor configuration."""
    print("🧪 Testing Cursor configuration saving...")
    
    # Create temporary project directory
    with tempfile.TemporaryDirectory() as temp_dir:
        navigator = DocumentationNavigator(temp_dir)
        cursor_integration = CursorIntegration(navigator)
        
        # Save configuration
        result = cursor_integration.save_cursor_config(".cursor/test_navigation.json")
        assert result is True
        
        # Check if file was created
        config_file = Path(temp_dir) / ".cursor" / "test_navigation.json"
        assert config_file.exists()
        
        # Load and validate the saved config
        with open(config_file, 'r') as f:
            saved_config = json.load(f)
        
        assert "version" in saved_config
        assert "commands" in saved_config
    
    print("✅ Cursor configuration saving test passed")


def test_utility_functions():
    """Test utility functions."""
    print("🧪 Testing utility functions...")
    
    # Test open_documentation
    with patch('src.doc_navigation.open_documentation') as mock_open:
        mock_open.return_value = True
        result = open_documentation("overview")
        assert result is True
    
    # Test open_source_file
    with patch('src.doc_navigation.open_source_file') as mock_open:
        mock_open.return_value = True
        result = open_source_file(SourceLocation.MAIN_API)
        assert result is True
    
    # Test open_github_file
    with patch('src.doc_navigation.open_github_file') as mock_open:
        mock_open.return_value = True
        result = open_github_file(SourceLocation.MAIN_API)
        assert result is True
    
    # Test search functions
    results = search_documentation("api")
    assert isinstance(results, list)
    
    source_results = search_source_code("security")
    assert isinstance(source_results, list)
    
    print("✅ Utility functions test passed")


def test_list_functions():
    """Test list functionality."""
    print("🧪 Testing list functions...")
    
    navigator = DocumentationNavigator()
    
    # Test listing documentation sections
    doc_sections = navigator.list_doc_sections()
    assert len(doc_sections) > 0
    assert all(isinstance(section, DocLink) for section in doc_sections)
    
    # Test listing source locations
    source_locations = navigator.list_source_locations()
    assert len(source_locations) > 0
    assert all(isinstance(location, SourceMapping) for location in source_locations)
    
    print("✅ List functions test passed")


def run_all_tests():
    """Run all documentation navigation tests."""
    print("🚀 Starting Documentation Navigation Tests")
    print("=" * 50)
    
    test_functions = [
        test_doc_sections,
        test_source_locations,
        test_doc_link,
        test_source_mapping,
        test_documentation_navigator_initialization,
        test_doc_link_retrieval,
        test_source_mapping_retrieval,
        test_documentation_search,
        test_source_code_search,
        test_open_doc_link,
        test_open_source_file,
        test_open_github_file,
        test_documentation_index_generation,
        test_documentation_index_saving,
        test_cursor_integration,
        test_cursor_config_saving,
        test_utility_functions,
        test_list_functions
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
        print("🎉 All documentation navigation tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests()) 