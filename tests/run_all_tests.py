#!/usr/bin/env python3
"""
Comprehensive Test Runner for Qwen-Agent Chatbot System
Runs all test suites and generates detailed reports.
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestRunner:
    """Test runner for the Qwen-Agent chatbot system."""
    
    def __init__(self):
        self.project_root = project_root
        self.tests_dir = project_root / "tests"
        self.scripts_dir = self.tests_dir / "scripts"
        self.results_dir = self.tests_dir / "results"
        self.results_file = self.results_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Ensure results directory exists
        self.results_dir.mkdir(exist_ok=True)
        
        # Test configuration
        self.test_scripts = [
            {
                "name": "API Tests",
                "file": "test_api.py",
                "description": "Core API functionality tests",
                "category": "integration"
            },
            {
                "name": "Multi-Modal Tests", 
                "file": "test_multimodal.py",
                "description": "Multi-modal processing and file handling tests",
                "category": "integration"
            },
            {
                "name": "Web Interface Tests",
                "file": "test_webui.py", 
                "description": "Web UI functionality and API integration tests",
                "category": "e2e"
            },
            {
                "name": "Task Management Tests",
                "file": "test_tasks.py",
                "description": "Task segmentation and management tests", 
                "category": "unit"
            },
            {
                "name": "API Security Tests",
                "file": "test_api_security.py",
                "description": "Rate limiting, security headers, and API interface tests",
                "category": "security"
            }
        ]
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "success_rate": 0.0
            },
            "test_suites": [],
            "system_info": self._get_system_info()
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for the test report."""
        try:
            import platform
            import psutil
            
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_usage": psutil.disk_usage('/').percent
            }
        except ImportError:
            return {
                "platform": "Unknown",
                "python_version": "Unknown",
                "note": "psutil not available for detailed system info"
            }
    
    def _check_server_status(self) -> bool:
        """Check if the API server is running."""
        try:
            import requests
            response = requests.get("http://localhost:8002/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _start_server(self) -> bool:
        """Start the API server if not running."""
        if self._check_server_status():
            print("✅ API server is already running")
            return True
        
        print("🚀 Starting API server...")
        try:
            # Start server in background
            process = subprocess.Popen(
                ["uv", "run", "python", "main.py", "--mode", "api"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            for _ in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                if self._check_server_status():
                    print("✅ API server started successfully")
                    return True
            
            print("❌ Failed to start API server")
            return False
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def _run_test_script(self, test_info: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test script and capture results."""
        script_path = self.scripts_dir / test_info["file"]
        
        if not script_path.exists():
            return {
                "name": test_info["name"],
                "status": "error",
                "error": f"Test file not found: {test_info['file']}",
                "duration": 0,
                "output": ""
            }
        
        print(f"\n🧪 Running {test_info['name']}...")
        start_time = time.time()
        
        try:
            # Run the test script
            result = subprocess.run(
                ["uv", "run", "python", str(script_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            
            # Parse the output to determine pass/fail
            output = result.stdout + result.stderr
            status = "passed" if result.returncode == 0 else "failed"
            
            # Count test results from output
            passed_count = output.count("✅")
            failed_count = output.count("❌")
            
            print(f"   Duration: {duration:.2f}s")
            print(f"   Status: {status.upper()}")
            print(f"   Passed: {passed_count}, Failed: {failed_count}")
            
            return {
                "name": test_info["name"],
                "category": test_info["category"],
                "description": test_info["description"],
                "status": status,
                "duration": duration,
                "return_code": result.returncode,
                "passed_count": passed_count,
                "failed_count": failed_count,
                "output": output,
                "error": result.stderr if result.stderr else None
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"   Duration: {duration:.2f}s")
            print("   Status: TIMEOUT")
            
            return {
                "name": test_info["name"],
                "category": test_info["category"],
                "description": test_info["description"],
                "status": "timeout",
                "duration": duration,
                "output": "Test timed out after 5 minutes",
                "error": "Timeout"
            }
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"   Duration: {duration:.2f}s")
            print(f"   Status: ERROR - {e}")
            
            return {
                "name": test_info["name"],
                "category": test_info["category"],
                "description": test_info["description"],
                "status": "error",
                "duration": duration,
                "output": "",
                "error": str(e)
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites and generate comprehensive report."""
        print("🚀 Starting Comprehensive Test Suite")
        print("=" * 60)
        
        # Check and start server
        if not self._start_server():
            print("❌ Cannot run tests without API server")
            return self.results
        
        # Run each test suite
        for test_info in self.test_scripts:
            result = self._run_test_script(test_info)
            self.results["test_suites"].append(result)
        
        # Calculate summary statistics
        self._calculate_summary()
        
        # Save results
        self._save_results()
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _calculate_summary(self):
        """Calculate summary statistics from test results."""
        total_tests = len(self.results["test_suites"])
        passed = sum(1 for suite in self.results["test_suites"] if suite["status"] == "passed")
        failed = total_tests - passed
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0
        }
    
    def _save_results(self):
        """Save test results to JSON file."""
        try:
            with open(self.results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n📊 Test results saved to: {self.results_file}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    def _print_summary(self):
        """Print a summary of test results."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        summary = self.results["summary"]
        print(f"Total Test Suites: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        print(f"\n📁 Results saved to: {self.results_file}")
        
        # Print individual test results
        print(f"\n📋 Individual Test Results:")
        for suite in self.results["test_suites"]:
            status_icon = "✅" if suite["status"] == "passed" else "❌"
            print(f"  {status_icon} {suite['name']} ({suite['category']}) - {suite['status'].upper()}")
            if suite.get("passed_count") is not None:
                print(f"     Passed: {suite['passed_count']}, Failed: {suite['failed_count']}")
        
        # Overall result
        if summary["success_rate"] == 100:
            print(f"\n🎉 ALL TESTS PASSED! Success rate: {summary['success_rate']:.1f}%")
        elif summary["success_rate"] >= 80:
            print(f"\n✅ MOST TESTS PASSED! Success rate: {summary['success_rate']:.1f}%")
        else:
            print(f"\n⚠️  MANY TESTS FAILED! Success rate: {summary['success_rate']:.1f}%")

def main():
    """Main function to run all tests."""
    runner = TestRunner()
    results = runner.run_all_tests()
    
    # Exit with appropriate code
    if results["summary"]["success_rate"] == 100:
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main() 