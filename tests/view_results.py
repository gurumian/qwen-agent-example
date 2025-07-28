#!/usr/bin/env python3
"""
Test Results Viewer
View and analyze test results from the results directory.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def list_results(results_dir: Path) -> List[Path]:
    """List all test result files."""
    return sorted(results_dir.glob("test_results_*.json"), reverse=True)

def load_result(result_file: Path) -> Dict[str, Any]:
    """Load a test result file."""
    with open(result_file, 'r') as f:
        return json.load(f)

def print_summary(result: Dict[str, Any]):
    """Print a summary of test results."""
    summary = result["summary"]
    timestamp = datetime.fromisoformat(result["timestamp"])
    
    print(f"📊 Test Results - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"Total Test Suites: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    
    # System info
    if "system_info" in result:
        sys_info = result["system_info"]
        print(f"\n🖥️  System Info:")
        print(f"  Platform: {sys_info.get('platform', 'Unknown')}")
        print(f"  Python: {sys_info.get('python_version', 'Unknown')}")
        if "cpu_count" in sys_info:
            print(f"  CPU Cores: {sys_info['cpu_count']}")
        if "memory_total" in sys_info:
            memory_gb = sys_info['memory_total'] / (1024**3)
            print(f"  Memory: {memory_gb:.1f} GB")
        if "disk_usage" in sys_info:
            print(f"  Disk Usage: {sys_info['disk_usage']:.1f}%")

def print_detailed_results(result: Dict[str, Any]):
    """Print detailed test results."""
    print(f"\n📋 Detailed Results:")
    print("-" * 60)
    
    for suite in result["test_suites"]:
        status_icon = "✅" if suite["status"] == "passed" else "❌"
        print(f"{status_icon} {suite['name']} ({suite['category']})")
        print(f"   Duration: {suite['duration']:.2f}s")
        print(f"   Status: {suite['status'].upper()}")
        
        if suite.get("passed_count") is not None:
            print(f"   Passed: {suite['passed_count']}, Failed: {suite['failed_count']}")
        
        if suite.get("error"):
            print(f"   Error: {suite['error']}")
        
        print()

def compare_results(results: List[Dict[str, Any]]):
    """Compare multiple test results."""
    if len(results) < 2:
        print("Need at least 2 results to compare")
        return
    
    print("📈 Results Comparison:")
    print("-" * 60)
    
    for i, result in enumerate(results):
        summary = result["summary"]
        timestamp = datetime.fromisoformat(result["timestamp"])
        print(f"Run {i+1} ({timestamp.strftime('%H:%M:%S')}): {summary['success_rate']:.1f}% success rate")

def main():
    """Main function."""
    results_dir = Path(__file__).parent / "results"
    
    if not results_dir.exists():
        print("❌ No results directory found")
        sys.exit(1)
    
    result_files = list_results(results_dir)
    
    if not result_files:
        print("❌ No test result files found")
        sys.exit(1)
    
    # Load the most recent result
    latest_result = load_result(result_files[0])
    
    print_summary(latest_result)
    print_detailed_results(latest_result)
    
    # Show comparison if multiple results exist
    if len(result_files) > 1:
        print("=" * 60)
        recent_results = []
        for result_file in result_files[:3]:  # Last 3 results
            recent_results.append(load_result(result_file))
        compare_results(recent_results)
    
    print(f"\n📁 Results directory: {results_dir}")
    print(f"📄 Latest result: {result_files[0].name}")

if __name__ == "__main__":
    main() 