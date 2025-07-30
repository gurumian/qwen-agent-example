#!/usr/bin/env python3
"""
Simple Docker Testing Script for Qwen-Agent Chatbot
Tests Docker build, container startup, health checks, and API functionality
"""

import os
import sys
import time
import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional

class SimpleDockerTester:
    def __init__(self):
        self.project_name = "qwen-agent-chatbot"
        self.port = 8002
        self.ollama_port = 11434
        
    def print_status(self, message: str, status: str = "INFO"):
        """Print formatted status message"""
        colors = {
            "INFO": "\033[94m",    # Blue
            "SUCCESS": "\033[92m", # Green
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
        }
        color = colors.get(status, colors["INFO"])
        reset = "\033[0m"
        print(f"{color}[{status}]{reset} {message}")
    
    def run_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run shell command and return result"""
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=check)
            return result
        except subprocess.CalledProcessError as e:
            self.print_status(f"Command failed: {' '.join(command)}", "ERROR")
            self.print_status(f"Error: {e.stderr}", "ERROR")
            if check:
                raise
            return e
    
    def test_docker_installation(self) -> bool:
        """Test if Docker is properly installed and running"""
        self.print_status("Testing Docker installation...")
        
        try:
            # Test Docker daemon
            result = self.run_command(["docker", "version"])
            if result.returncode == 0:
                self.print_status("Docker daemon is running", "SUCCESS")
                return True
            else:
                self.print_status("Docker daemon is not running", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"Docker test failed: {e}", "ERROR")
            return False
    
    def test_docker_compose(self) -> bool:
        """Test if Docker Compose is available"""
        self.print_status("Testing Docker Compose...")
        
        try:
            result = self.run_command(["docker-compose", "--version"])
            if result.returncode == 0:
                self.print_status("Docker Compose is available", "SUCCESS")
                return True
            else:
                self.print_status("Docker Compose is not available", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"Docker Compose test failed: {e}", "ERROR")
            return False
    
    def test_dockerfile(self) -> bool:
        """Test Dockerfile syntax and build context"""
        self.print_status("Testing Dockerfile...")
        
        if not Path("Dockerfile").exists():
            self.print_status("Dockerfile not found", "ERROR")
            return False
        
        if not Path("docker-compose.yml").exists():
            self.print_status("docker-compose.yml not found", "ERROR")
            return False
        
        # Check if required files exist
        required_files = ["pyproject.toml", "uv.lock", "main.py"]
        for file in required_files:
            if not Path(file).exists():
                self.print_status(f"Required file {file} not found", "ERROR")
                return False
        
        self.print_status("Dockerfile and required files found", "SUCCESS")
        return True
    
    def test_docker_build(self) -> bool:
        """Test Docker image build"""
        self.print_status("Testing Docker image build...")
        
        try:
            # Build the image
            result = self.run_command([
                "docker", "build", "-t", f"{self.project_name}:test", "."
            ])
            
            if result.returncode == 0:
                self.print_status("Docker image built successfully", "SUCCESS")
                return True
            else:
                self.print_status("Docker build failed", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"Docker build test failed: {e}", "ERROR")
            return False
    
    def test_docker_compose_build(self) -> bool:
        """Test Docker Compose build"""
        self.print_status("Testing Docker Compose build...")
        
        try:
            # Build with docker-compose
            result = self.run_command(["docker-compose", "build"])
            
            if result.returncode == 0:
                self.print_status("Docker Compose build successful", "SUCCESS")
                return True
            else:
                self.print_status("Docker Compose build failed", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"Docker Compose build test failed: {e}", "ERROR")
            return False
    
    def test_container_startup(self) -> bool:
        """Test container startup and basic functionality"""
        self.print_status("Testing container startup...")
        
        try:
            # Start services with docker-compose
            result = self.run_command(["docker-compose", "up", "-d"])
            
            if result.returncode != 0:
                self.print_status("Failed to start containers", "ERROR")
                return False
            
            # Wait for containers to be ready
            time.sleep(15)
            
            # Check if containers are running
            result = self.run_command(["docker-compose", "ps"])
            if result.returncode == 0:
                self.print_status("Containers started successfully", "SUCCESS")
                return True
            else:
                self.print_status("Container startup check failed", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"Container startup test failed: {e}", "ERROR")
            return False
    
    def test_health_checks(self) -> bool:
        """Test health check endpoints"""
        self.print_status("Testing health checks...")
        
        try:
            # Test Ollama health
            ollama_health_url = f"http://localhost:{self.ollama_port}/v1/models"
            response = requests.get(ollama_health_url, timeout=10)
            
            if response.status_code == 200:
                self.print_status("Ollama health check passed", "SUCCESS")
            else:
                self.print_status(f"Ollama health check failed: {response.status_code}", "WARNING")
            
            # Test Qwen Agent health
            agent_health_url = f"http://localhost:{self.port}/health"
            response = requests.get(agent_health_url, timeout=10)
            
            if response.status_code == 200:
                self.print_status("Qwen Agent health check passed", "SUCCESS")
                return True
            else:
                self.print_status(f"Qwen Agent health check failed: {response.status_code}", "ERROR")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_status(f"Health check test failed: {e}", "ERROR")
            return False
    
    def test_api_functionality(self) -> bool:
        """Test basic API functionality"""
        self.print_status("Testing API functionality...")
        
        try:
            # Test API root endpoint
            api_url = f"http://localhost:{self.port}/"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                self.print_status("API root endpoint working", "SUCCESS")
            else:
                self.print_status(f"API root endpoint failed: {response.status_code}", "WARNING")
            
            # Test chat endpoint
            chat_url = f"http://localhost:{self.port}/chat"
            chat_data = {
                "message": "Hello, this is a test message",
                "model": "qwen3:14b"
            }
            
            response = requests.post(chat_url, json=chat_data, timeout=30)
            
            if response.status_code in [200, 201]:
                self.print_status("Chat API endpoint working", "SUCCESS")
                return True
            else:
                self.print_status(f"Chat API endpoint failed: {response.status_code}", "WARNING")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_status(f"API functionality test failed: {e}", "ERROR")
            return False
    
    def test_container_logs(self) -> bool:
        """Test container logs for errors"""
        self.print_status("Checking container logs...")
        
        try:
            # Get logs from qwen-agent-chatbot container
            result = self.run_command([
                "docker-compose", "logs", "qwen-agent-chatbot"
            ])
            
            if result.returncode == 0:
                logs = result.stdout
                if "error" in logs.lower() or "exception" in logs.lower():
                    self.print_status("Found errors in container logs", "WARNING")
                    print(logs[-500:])  # Show last 500 characters
                else:
                    self.print_status("Container logs look clean", "SUCCESS")
                return True
            else:
                self.print_status("Failed to get container logs", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"Container logs test failed: {e}", "ERROR")
            return False
    
    def cleanup(self):
        """Clean up test containers and images"""
        self.print_status("Cleaning up test resources...")
        
        try:
            # Stop and remove containers
            self.run_command(["docker-compose", "down"], check=False)
            
            # Remove test image
            self.run_command([
                "docker", "rmi", f"{self.project_name}:test"
            ], check=False)
            
            self.print_status("Cleanup completed", "SUCCESS")
        except Exception as e:
            self.print_status(f"Cleanup failed: {e}", "WARNING")
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all Docker tests"""
        self.print_status("Starting Docker tests...", "INFO")
        
        results = {}
        
        # Test Docker installation
        results["docker_installation"] = self.test_docker_installation()
        
        # Test Docker Compose
        results["docker_compose"] = self.test_docker_compose()
        
        # Test Dockerfile
        results["dockerfile"] = self.test_dockerfile()
        
        # Test Docker build
        results["docker_build"] = self.test_docker_build()
        
        # Test Docker Compose build
        results["docker_compose_build"] = self.test_docker_compose_build()
        
        # Test container startup
        results["container_startup"] = self.test_container_startup()
        
        # Test health checks
        results["health_checks"] = self.test_health_checks()
        
        # Test API functionality
        results["api_functionality"] = self.test_api_functionality()
        
        # Test container logs
        results["container_logs"] = self.test_container_logs()
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test results summary"""
        self.print_status("Test Results Summary:", "INFO")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title():<25} {status}")
            if result:
                passed += 1
        
        print("=" * 50)
        print(f"Total: {total}, Passed: {passed}, Failed: {total - passed}")
        
        if passed == total:
            self.print_status("All tests passed! 🎉", "SUCCESS")
        else:
            self.print_status(f"{total - passed} test(s) failed", "WARNING")

def main():
    """Main function"""
    tester = SimpleDockerTester()
    
    try:
        # Run all tests
        results = tester.run_all_tests()
        
        # Print summary
        tester.print_summary(results)
        
        # Ask user if they want to clean up
        response = input("\nDo you want to clean up test containers? (y/n): ")
        if response.lower() in ['y', 'yes']:
            tester.cleanup()
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        tester.cleanup()
    except Exception as e:
        print(f"Test failed with error: {e}")
        tester.cleanup()

if __name__ == "__main__":
    main() 