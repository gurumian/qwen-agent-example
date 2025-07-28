"""
Performance benchmarking test suite

Tests system performance including response latency, throughput, and resource usage.
"""

import sys
import os
import time
import json
import psutil
import threading
import concurrent.futures
import requests
import statistics
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import Config


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    test_name: str
    duration: float
    requests_per_second: float
    average_response_time: float
    min_response_time: float
    max_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    success_rate: float
    error_count: int
    total_requests: int


class PerformanceBenchmark:
    """Performance benchmarking framework."""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.results: List[PerformanceMetrics] = []
        
    def measure_response_time(self, endpoint: str, method: str = "GET", 
                            data: Dict = None, headers: Dict = None) -> Tuple[float, bool]:
        """Measure response time for a single request."""
        start_time = time.time()
        success = False
        
        try:
            if method.upper() == "GET":
                response = requests.get(f"{self.base_url}{endpoint}", 
                                     headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(f"{self.base_url}{endpoint}", 
                                      json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = response.status_code < 400
        except Exception as e:
            print(f"Request failed: {e}")
            success = False
        
        duration = time.time() - start_time
        return duration, success
    
    def get_system_metrics(self) -> Tuple[float, float]:
        """Get current system memory and CPU usage."""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent()
        return memory_mb, cpu_percent
    
    def run_single_request_test(self, endpoint: str, method: str = "GET", 
                              data: Dict = None, test_name: str = None) -> PerformanceMetrics:
        """Run a single request performance test."""
        if test_name is None:
            test_name = f"{method}_{endpoint.replace('/', '_')}"
        
        print(f"🧪 Running single request test: {test_name}")
        
        # Measure system metrics before
        memory_before, cpu_before = self.get_system_metrics()
        
        # Make request
        duration, success = self.measure_response_time(endpoint, method, data)
        
        # Measure system metrics after
        memory_after, cpu_after = self.get_system_metrics()
        
        metrics = PerformanceMetrics(
            test_name=test_name,
            duration=duration,
            requests_per_second=1.0 / duration if duration > 0 else 0,
            average_response_time=duration,
            min_response_time=duration,
            max_response_time=duration,
            median_response_time=duration,
            p95_response_time=duration,
            p99_response_time=duration,
            memory_usage_mb=memory_after,
            cpu_usage_percent=cpu_after,
            success_rate=1.0 if success else 0.0,
            error_count=0 if success else 1,
            total_requests=1
        )
        
        print(f"✅ {test_name}: {duration:.3f}s, Success: {success}")
        return metrics
    
    def run_load_test(self, endpoint: str, num_requests: int, 
                     concurrent_requests: int = 1, method: str = "GET",
                     data: Dict = None, test_name: str = None) -> PerformanceMetrics:
        """Run a load test with multiple concurrent requests."""
        if test_name is None:
            test_name = f"load_test_{method}_{endpoint.replace('/', '_')}_{num_requests}req"
        
        print(f"🧪 Running load test: {test_name}")
        print(f"   Requests: {num_requests}, Concurrent: {concurrent_requests}")
        
        # Measure system metrics before
        memory_before, cpu_before = self.get_system_metrics()
        
        response_times = []
        success_count = 0
        error_count = 0
        start_time = time.time()
        
        def make_request():
            nonlocal success_count, error_count
            duration, success = self.measure_response_time(endpoint, method, data)
            response_times.append(duration)
            if success:
                success_count += 1
            else:
                error_count += 1
        
        # Run concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            concurrent.futures.wait(futures)
        
        total_duration = time.time() - start_time
        
        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            median_response_time = statistics.median(response_times)
            
            # Calculate percentiles
            sorted_times = sorted(response_times)
            p95_index = int(0.95 * len(sorted_times))
            p99_index = int(0.99 * len(sorted_times))
            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
            p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time
        else:
            avg_response_time = min_response_time = max_response_time = median_response_time = 0
            p95_response_time = p99_response_time = 0
        
        # Measure system metrics after
        memory_after, cpu_after = self.get_system_metrics()
        
        metrics = PerformanceMetrics(
            test_name=test_name,
            duration=total_duration,
            requests_per_second=num_requests / total_duration if total_duration > 0 else 0,
            average_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            memory_usage_mb=memory_after,
            cpu_usage_percent=cpu_after,
            success_rate=success_count / num_requests if num_requests > 0 else 0,
            error_count=error_count,
            total_requests=num_requests
        )
        
        print(f"✅ {test_name}: {total_duration:.3f}s, {metrics.requests_per_second:.2f} req/s, "
              f"Success: {metrics.success_rate:.1%}")
        
        return metrics
    
    def run_scalability_test(self, endpoint: str, base_requests: int = 10,
                           max_concurrent: int = 10, method: str = "GET",
                           data: Dict = None) -> List[PerformanceMetrics]:
        """Run scalability test with increasing concurrent load."""
        print(f"🧪 Running scalability test: {endpoint}")
        
        results = []
        
        for concurrent in range(1, max_concurrent + 1):
            test_name = f"scalability_{method}_{endpoint.replace('/', '_')}_{concurrent}concurrent"
            metrics = self.run_load_test(
                endpoint=endpoint,
                num_requests=base_requests * concurrent,
                concurrent_requests=concurrent,
                method=method,
                data=data,
                test_name=test_name
            )
            results.append(metrics)
            
            # Brief pause between tests
            time.sleep(1)
        
        return results
    
    def run_stress_test(self, endpoint: str, duration_seconds: int = 60,
                       requests_per_second: int = 10, method: str = "GET",
                       data: Dict = None) -> PerformanceMetrics:
        """Run a stress test for a specified duration."""
        test_name = f"stress_test_{method}_{endpoint.replace('/', '_')}_{duration_seconds}s"
        print(f"🧪 Running stress test: {test_name}")
        print(f"   Duration: {duration_seconds}s, Rate: {requests_per_second} req/s")
        
        response_times = []
        success_count = 0
        error_count = 0
        start_time = time.time()
        
        def make_request():
            nonlocal success_count, error_count
            duration, success = self.measure_response_time(endpoint, method, data)
            response_times.append(duration)
            if success:
                success_count += 1
            else:
                error_count += 1
        
        # Calculate request interval
        interval = 1.0 / requests_per_second
        
        # Run stress test
        with concurrent.futures.ThreadPoolExecutor(max_workers=requests_per_second * 2) as executor:
            futures = []
            request_count = 0
            
            while time.time() - start_time < duration_seconds:
                future = executor.submit(make_request)
                futures.append(future)
                request_count += 1
                
                # Wait for next request interval
                time.sleep(interval)
            
            # Wait for remaining requests to complete
            concurrent.futures.wait(futures)
        
        total_duration = time.time() - start_time
        
        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            median_response_time = statistics.median(response_times)
            
            sorted_times = sorted(response_times)
            p95_index = int(0.95 * len(sorted_times))
            p99_index = int(0.99 * len(sorted_times))
            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
            p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time
        else:
            avg_response_time = min_response_time = max_response_time = median_response_time = 0
            p95_response_time = p99_response_time = 0
        
        # Measure system metrics
        memory_after, cpu_after = self.get_system_metrics()
        
        metrics = PerformanceMetrics(
            test_name=test_name,
            duration=total_duration,
            requests_per_second=len(response_times) / total_duration if total_duration > 0 else 0,
            average_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            memory_usage_mb=memory_after,
            cpu_usage_percent=cpu_after,
            success_rate=success_count / len(response_times) if response_times else 0,
            error_count=error_count,
            total_requests=len(response_times)
        )
        
        print(f"✅ {test_name}: {total_duration:.3f}s, {metrics.requests_per_second:.2f} req/s, "
              f"Success: {metrics.success_rate:.1%}")
        
        return metrics
    
    def save_results(self, filename: str = None):
        """Save performance test results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_results_{timestamp}.json"
        
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "results": [
                {
                    "test_name": result.test_name,
                    "duration": result.duration,
                    "requests_per_second": result.requests_per_second,
                    "average_response_time": result.average_response_time,
                    "min_response_time": result.min_response_time,
                    "max_response_time": result.max_response_time,
                    "median_response_time": result.median_response_time,
                    "p95_response_time": result.p95_response_time,
                    "p99_response_time": result.p99_response_time,
                    "memory_usage_mb": result.memory_usage_mb,
                    "cpu_usage_percent": result.cpu_usage_percent,
                    "success_rate": result.success_rate,
                    "error_count": result.error_count,
                    "total_requests": result.total_requests
                }
                for result in self.results
            ]
        }
        
        # Save to tests/results directory
        results_dir = project_root / "tests" / "results"
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"📊 Results saved to: {filepath}")
        return filepath


def test_health_endpoint_performance():
    """Test health endpoint performance."""
    print("🧪 Testing health endpoint performance...")
    
    benchmark = PerformanceBenchmark()
    
    # Single request test
    metrics = benchmark.run_single_request_test("/health")
    benchmark.results.append(metrics)
    
    # Load test
    metrics = benchmark.run_load_test("/health", num_requests=50, concurrent_requests=5)
    benchmark.results.append(metrics)
    
    print("✅ Health endpoint performance test completed")


def test_api_info_performance():
    """Test API info endpoint performance."""
    print("🧪 Testing API info endpoint performance...")
    
    benchmark = PerformanceBenchmark()
    
    # Single request test
    metrics = benchmark.run_single_request_test("/api/info")
    benchmark.results.append(metrics)
    
    # Load test
    metrics = benchmark.run_load_test("/api/info", num_requests=30, concurrent_requests=3)
    benchmark.results.append(metrics)
    
    print("✅ API info endpoint performance test completed")


def test_chat_endpoint_performance():
    """Test chat endpoint performance."""
    print("🧪 Testing chat endpoint performance...")
    
    benchmark = PerformanceBenchmark()
    
    # Test data
    chat_data = {
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "stream": False
    }
    
    # Single request test
    metrics = benchmark.run_single_request_test("/chat", method="POST", data=chat_data)
    benchmark.results.append(metrics)
    
    # Load test (smaller load for chat endpoint)
    metrics = benchmark.run_load_test("/chat", num_requests=10, concurrent_requests=2, 
                                    method="POST", data=chat_data)
    benchmark.results.append(metrics)
    
    print("✅ Chat endpoint performance test completed")


def test_scalability():
    """Test system scalability."""
    print("🧪 Testing system scalability...")
    
    benchmark = PerformanceBenchmark()
    
    # Scalability test for health endpoint
    scalability_results = benchmark.run_scalability_test("/health", base_requests=5, max_concurrent=5)
    benchmark.results.extend(scalability_results)
    
    print("✅ Scalability test completed")


def test_stress_conditions():
    """Test system under stress conditions."""
    print("🧪 Testing system under stress conditions...")
    
    benchmark = PerformanceBenchmark()
    
    # Short stress test
    stress_metrics = benchmark.run_stress_test("/health", duration_seconds=30, requests_per_second=5)
    benchmark.results.append(stress_metrics)
    
    print("✅ Stress test completed")


def run_all_performance_tests():
    """Run all performance tests."""
    print("🚀 Starting Performance Benchmarking Tests")
    print("=" * 50)
    
    benchmark = PerformanceBenchmark()
    
    try:
        # Run individual endpoint tests
        test_health_endpoint_performance()
        test_api_info_performance()
        test_chat_endpoint_performance()
        
        # Run scalability and stress tests
        test_scalability()
        test_stress_conditions()
        
        # Save results
        results_file = benchmark.save_results()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Performance Test Summary")
        print("=" * 50)
        
        for result in benchmark.results:
            print(f"📈 {result.test_name}")
            print(f"   Duration: {result.duration:.3f}s")
            print(f"   Requests/sec: {result.requests_per_second:.2f}")
            print(f"   Avg Response: {result.average_response_time:.3f}s")
            print(f"   Success Rate: {result.success_rate:.1%}")
            print(f"   Memory Usage: {result.memory_usage_mb:.1f}MB")
            print(f"   CPU Usage: {result.cpu_usage_percent:.1f}%")
            print()
        
        print(f"📁 Results saved to: {results_file}")
        print("🎉 Performance benchmarking completed!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_performance_tests()) 