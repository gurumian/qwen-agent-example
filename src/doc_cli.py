"""
Documentation Navigation CLI for Qwen-Agent Chatbot

This module provides a command-line interface for quick navigation to
documentation, source code, and GitHub repository links.
"""

import argparse
import sys
from typing import List, Optional
from pathlib import Path

from .doc_navigation import (
    doc_navigator, SourceLocation, DocSection,
    open_documentation, open_source_file, open_github_file,
    search_documentation, search_source_code,
    generate_documentation_index, setup_cursor_integration
)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Qwen-Agent Chatbot Documentation Navigator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Open documentation sections
  python -m src.doc_cli doc overview
  python -m src.doc_cli doc api_reference
  python -m src.doc_cli doc extensibility

  # Open source files
  python -m src.doc_cli source main_api
  python -m src.doc_cli source security
  python -m src.doc_cli source extensibility

  # Open files on GitHub
  python -m src.doc_cli github main_api
  python -m src.doc_cli github security

  # Search documentation
  python -m src.doc_cli search "custom tools"
  python -m src.doc_cli search "security"

  # List available options
  python -m src.doc_cli list docs
  python -m src.doc_cli list source
  python -m src.doc_cli list all

  # Setup and utilities
  python -m src.doc_cli setup cursor
  python -m src.doc_cli setup index
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Documentation commands
    doc_parser = subparsers.add_parser('doc', help='Open documentation sections')
    doc_parser.add_argument('section', help='Documentation section to open')
    
    # Source file commands
    source_parser = subparsers.add_parser('source', help='Open source files')
    source_parser.add_argument('location', help='Source location to open')
    source_parser.add_argument('--line', '-l', type=int, help='Line number to jump to')
    
    # GitHub commands
    github_parser = subparsers.add_parser('github', help='Open files on GitHub')
    github_parser.add_argument('location', help='Source location to open on GitHub')
    github_parser.add_argument('--line', '-l', type=int, help='Line number to jump to')
    
    # Search commands
    search_parser = subparsers.add_parser('search', help='Search documentation and source code')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--type', '-t', choices=['docs', 'source', 'all'], 
                              default='all', help='Search type')
    
    # List commands
    list_parser = subparsers.add_parser('list', help='List available options')
    list_parser.add_argument('type', choices=['docs', 'source', 'all'], 
                            help='Type of items to list')
    
    # Setup commands
    setup_parser = subparsers.add_parser('setup', help='Setup utilities')
    setup_parser.add_argument('action', choices=['cursor', 'index'], 
                             help='Setup action to perform')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'doc':
            return handle_doc_command(args.section)
        elif args.command == 'source':
            return handle_source_command(args.location, args.line)
        elif args.command == 'github':
            return handle_github_command(args.location, args.line)
        elif args.command == 'search':
            return handle_search_command(args.query, args.type)
        elif args.command == 'list':
            return handle_list_command(args.type)
        elif args.command == 'setup':
            return handle_setup_command(args.action)
        else:
            parser.print_help()
            return 1
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_doc_command(section: str) -> int:
    """Handle documentation command."""
    print(f"Opening documentation: {section}")
    
    if open_documentation(section):
        print(f"✅ Successfully opened {section} documentation")
        return 0
    else:
        print(f"❌ Failed to open {section} documentation")
        return 1


def handle_source_command(location: str, line_number: Optional[int]) -> int:
    """Handle source file command."""
    try:
        source_location = SourceLocation(location)
    except ValueError:
        print(f"❌ Invalid source location: {location}")
        print("Available locations:")
        for loc in SourceLocation:
            print(f"  - {loc.value}")
        return 1
    
    print(f"Opening source file: {location}")
    if line_number:
        print(f"Jumping to line: {line_number}")
    
    if open_source_file(source_location, line_number):
        print(f"✅ Successfully opened {location} source file")
        return 0
    else:
        print(f"❌ Failed to open {location} source file")
        return 1


def handle_github_command(location: str, line_number: Optional[int]) -> int:
    """Handle GitHub command."""
    try:
        source_location = SourceLocation(location)
    except ValueError:
        print(f"❌ Invalid source location: {location}")
        print("Available locations:")
        for loc in SourceLocation:
            print(f"  - {loc.value}")
        return 1
    
    print(f"Opening GitHub file: {location}")
    if line_number:
        print(f"Jumping to line: {line_number}")
    
    if open_github_file(source_location, line_number):
        print(f"✅ Successfully opened {location} on GitHub")
        return 0
    else:
        print(f"❌ Failed to open {location} on GitHub")
        return 1


def handle_search_command(query: str, search_type: str) -> int:
    """Handle search command."""
    print(f"Searching for: {query}")
    print(f"Search type: {search_type}")
    print()
    
    if search_type in ['docs', 'all']:
        print("📚 Documentation Results:")
        doc_results = search_documentation(query)
        if doc_results:
            for result in doc_results:
                print(f"  📖 {result.title}")
                print(f"     {result.description}")
                print(f"     Tags: {', '.join(result.tags)}")
                print()
        else:
            print("  No documentation matches found")
            print()
    
    if search_type in ['source', 'all']:
        print("💻 Source Code Results:")
        source_results = search_source_code(query)
        if source_results:
            for result in source_results:
                print(f"  📁 {result.file_path}")
                print(f"     {result.description}")
                print(f"     Key functions: {', '.join(result.key_functions)}")
                print()
        else:
            print("  No source code matches found")
            print()
    
    return 0


def handle_list_command(list_type: str) -> int:
    """Handle list command."""
    if list_type in ['docs', 'all']:
        print("📚 Available Documentation Sections:")
        doc_links = doc_navigator.list_doc_sections()
        for link in doc_links:
            print(f"  📖 {link.section.value}: {link.title}")
            print(f"     {link.description}")
            print(f"     Tags: {', '.join(link.tags)}")
            print()
    
    if list_type in ['source', 'all']:
        print("💻 Available Source Locations:")
        source_mappings = doc_navigator.list_source_locations()
        for mapping in source_mappings:
            print(f"  📁 {mapping.location.value}: {mapping.file_path}")
            print(f"     {mapping.description}")
            print(f"     Key functions: {', '.join(mapping.key_functions)}")
            print()
    
    return 0


def handle_setup_command(action: str) -> int:
    """Handle setup command."""
    if action == 'cursor':
        print("Setting up Cursor IDE integration...")
        if setup_cursor_integration():
            print("✅ Successfully set up Cursor integration")
            print("Configuration saved to .cursor/navigation.json")
            return 0
        else:
            print("❌ Failed to set up Cursor integration")
            return 1
    
    elif action == 'index':
        print("Generating documentation index...")
        if generate_documentation_index():
            print("✅ Successfully generated documentation index")
            print("Index saved to docs/documentation_index.json")
            return 0
        else:
            print("❌ Failed to generate documentation index")
            return 1
    
    return 1


if __name__ == '__main__':
    sys.exit(main()) 