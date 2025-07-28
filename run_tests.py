#!/usr/bin/env python3
"""
Simple Test Runner for Qwen-Agent Chatbot System
Run this script from the project root to execute all tests.
"""

import sys
from pathlib import Path

# Add tests directory to path
tests_dir = Path(__file__).parent / "tests"
sys.path.insert(0, str(tests_dir))

if __name__ == "__main__":
    from run_all_tests import main
    main() 