# Tests Directory

This directory contains all test files and results for the Qwen-Agent Chatbot System.

## Directory Structure

```
tests/
├── README.md              # This file
├── run_all_tests.py       # Comprehensive test runner
├── scripts/               # Individual test scripts
│   ├── test_api.py        # Core API functionality tests
│   ├── test_multimodal.py # Multi-modal processing tests
│   ├── test_webui.py      # Web interface tests
│   └── test_tasks.py      # Task management tests
├── results/               # Test results and reports
│   └── test_results_*.json # Timestamped test result files
├── unit/                  # Unit tests (future use)
├── integration/           # Integration tests (future use)
└── e2e/                   # End-to-end tests (future use)
```

## Test Categories

### 🔧 Integration Tests
- **API Tests** (`test_api.py`): Core API functionality including health checks, chat, streaming, and agent management
- **Multi-Modal Tests** (`test_multimodal.py`): File processing, image analysis, document extraction, and base64 handling

### 🌐 End-to-End Tests
- **Web Interface Tests** (`test_webui.py`): Complete web UI functionality, task switching, and user interactions

### ⚙️ Unit Tests
- **Task Management Tests** (`test_tasks.py`): Task segmentation, configuration, and management functionality

## Running Tests

### Run All Tests
From the project root:
```bash
# Using the main test runner
python run_tests.py

# Or directly from tests directory
python tests/run_all_tests.py
```

### Run Individual Test Scripts
```bash
# API tests
uv run python tests/scripts/test_api.py

# Multi-modal tests
uv run python tests/scripts/test_multimodal.py

# Web interface tests
uv run python tests/scripts/test_webui.py

# Task management tests
uv run python tests/scripts/test_tasks.py
```

## Test Results

Test results are automatically saved to the `results/` directory with timestamps:
- `test_results_YYYYMMDD_HHMMSS.json`

### Result Format
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "summary": {
    "total_tests": 4,
    "passed": 4,
    "failed": 0,
    "success_rate": 100.0
  },
  "test_suites": [
    {
      "name": "API Tests",
      "category": "integration",
      "status": "passed",
      "duration": 5.23,
      "passed_count": 5,
      "failed_count": 0
    }
  ],
  "system_info": {
    "platform": "Linux-6.8.0-x86_64",
    "python_version": "3.11.0"
  }
}
```

## Test Requirements

### Prerequisites
- API server running on `http://localhost:8002`
- Ollama server running with `qwen3:14b` model
- All dependencies installed via `uv sync`

### Dependencies
- `requests`: For API testing
- `psutil`: For system information (optional)
- All project dependencies from `pyproject.toml`

## Adding New Tests

### 1. Create Test Script
Add your test script to `tests/scripts/` directory.

### 2. Update Test Runner
Add your test to the `test_scripts` list in `run_all_tests.py`:

```python
{
    "name": "Your Test Name",
    "file": "your_test.py",
    "description": "Description of what this test covers",
    "category": "unit|integration|e2e"
}
```

### 3. Test Script Template
```python
#!/usr/bin/env python3
"""
Your Test Description
"""

import requests
import time

def test_your_functionality():
    """Test description."""
    print("Testing your functionality...")
    try:
        # Your test code here
        response = requests.get("http://localhost:8002/health")
        if response.status_code == 200:
            print("✅ Your test passed")
        else:
            print("❌ Your test failed")
    except Exception as e:
        print(f"❌ Your test error: {e}")

def main():
    """Run all tests."""
    test_your_functionality()

if __name__ == "__main__":
    main()
```

## Test Best Practices

1. **Use Descriptive Names**: Test functions should clearly describe what they're testing
2. **Include Error Handling**: Always wrap test code in try-catch blocks
3. **Use Emojis**: Use ✅ for pass and ❌ for fail for clear visual feedback
4. **Clean Up**: Remove any temporary files created during tests
5. **Timeout Protection**: Long-running tests should have timeout protection
6. **Independent Tests**: Each test should be independent and not rely on other tests

## Troubleshooting

### Common Issues

1. **Server Not Running**: Ensure the API server is running on port 8002
2. **Ollama Not Available**: Make sure Ollama is running with the correct model
3. **Import Errors**: Ensure you're running tests from the correct directory
4. **Timeout Errors**: Some tests may take longer on slower systems

### Debug Mode
To run tests with more verbose output, modify the test scripts to include debug prints or use the `--verbose` flag if implemented.

## Continuous Integration

The test runner is designed to work with CI/CD pipelines:
- Exit code 0: All tests passed
- Exit code 1: Some tests failed

This allows for automated testing in deployment pipelines. 