#!/usr/bin/env python3
"""
Authentication and Security Tests
Test authentication, authorization, rate limiting, and security features.
"""

import requests
import time
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8002"

def test_health_endpoint():
    """Test health endpoint (should work without auth)."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint test passed")
            return True
        else:
            print(f"❌ Health endpoint test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint test error: {e}")
        return False

def test_authentication():
    """Test authentication endpoints."""
    print("\nTesting authentication...")
    
    # Test login
    try:
        response = requests.post(f"{BASE_URL}/auth/login", params={"username": "testuser"})
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                print("✅ Login test passed")
                token = data["access_token"]
                user = data["user"]
                
                # Test getting current user info
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
                if response.status_code == 200:
                    print("✅ Get current user test passed")
                else:
                    print(f"❌ Get current user test failed: {response.status_code}")
                    return False
                
                return True
            else:
                print("❌ Login response missing required fields")
                return False
        else:
            print(f"❌ Login test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

def test_api_key_creation():
    """Test API key creation."""
    print("\nTesting API key creation...")
    
    try:
        # First login to get a token
        response = requests.post(f"{BASE_URL}/auth/login", params={"username": "apiuser"})
        if response.status_code != 200:
            print("❌ Login failed for API key test")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create API key
        response = requests.post(
            f"{BASE_URL}/auth/api-key",
            params={"name": "Test API Key", "permissions": ["chat", "read"]},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if "api_key" in data:
                print("✅ API key creation test passed")
                return data["api_key"]
            else:
                print("❌ API key creation response missing API key")
                return None
        else:
            print(f"❌ API key creation test failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ API key creation test error: {e}")
        return None

def test_api_key_usage(api_key: str):
    """Test using the created API key."""
    print("\nTesting API key usage...")
    
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Test chat endpoint with API key
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "messages": [{"role": "user", "content": "Hello"}]
            },
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ API key usage test passed")
            return True
        else:
            print(f"❌ API key usage test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API key usage test error: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting functionality."""
    print("\nTesting rate limiting...")
    
    try:
        # Make multiple requests quickly to trigger rate limiting
        responses = []
        for i in range(65):  # More than the 60 per minute limit
            response = requests.get(f"{BASE_URL}/health")
            responses.append(response.status_code)
            
            if response.status_code == 429:  # Too Many Requests
                print(f"✅ Rate limiting triggered after {i+1} requests")
                return True
        
        print("❌ Rate limiting not triggered (may need adjustment)")
        return False
    except Exception as e:
        print(f"❌ Rate limiting test error: {e}")
        return False

def test_admin_endpoints():
    """Test admin-only endpoints."""
    print("\nTesting admin endpoints...")
    
    try:
        # Login as admin
        response = requests.post(f"{BASE_URL}/auth/login", params={"username": "admin"})
        if response.status_code != 200:
            print("❌ Admin login failed")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test admin stats endpoint
        response = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "total_users" in data and "total_api_keys" in data:
                print("✅ Admin stats endpoint test passed")
            else:
                print("❌ Admin stats response missing required fields")
                return False
        else:
            print(f"❌ Admin stats endpoint test failed: {response.status_code}")
            return False
        
        # Test users list endpoint
        response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            if isinstance(users, list):
                print("✅ Admin users endpoint test passed")
            else:
                print("❌ Admin users response not a list")
                return False
        else:
            print(f"❌ Admin users endpoint test failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Admin endpoints test error: {e}")
        return False

def test_security_headers():
    """Test security headers are present."""
    print("\nTesting security headers...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        headers = response.headers
        
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Referrer-Policy",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
        
        missing_headers = []
        for header in security_headers:
            if header not in headers:
                missing_headers.append(header)
        
        if not missing_headers:
            print("✅ Security headers test passed")
            return True
        else:
            print(f"❌ Missing security headers: {missing_headers}")
            return False
    except Exception as e:
        print(f"❌ Security headers test error: {e}")
        return False

def test_unauthorized_access():
    """Test unauthorized access is properly rejected."""
    print("\nTesting unauthorized access...")
    
    try:
        # Test accessing protected endpoint without auth
        response = requests.get(f"{BASE_URL}/auth/me")
        if response.status_code == 401:
            print("✅ Unauthorized access properly rejected")
            return True
        else:
            print(f"❌ Unauthorized access not properly rejected: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Unauthorized access test error: {e}")
        return False

def test_invalid_token():
    """Test invalid token is properly rejected."""
    print("\nTesting invalid token...")
    
    try:
        headers = {"Authorization": "Bearer invalid-token"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 401:
            print("✅ Invalid token properly rejected")
            return True
        else:
            print(f"❌ Invalid token not properly rejected: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invalid token test error: {e}")
        return False

def main():
    """Run all authentication and security tests."""
    print("🚀 Starting Authentication and Security Tests")
    print("=" * 60)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Authentication", test_authentication),
        ("API Key Creation", test_api_key_creation),
        ("Security Headers", test_security_headers),
        ("Unauthorized Access", test_unauthorized_access),
        ("Invalid Token", test_invalid_token),
        ("Admin Endpoints", test_admin_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_name == "API Key Creation":
                api_key = test_func()
                if api_key:
                    passed += 1
                    # Test API key usage
                    if test_api_key_usage(api_key):
                        passed += 1
                        total += 1
            else:
                if test_func():
                    passed += 1
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    # Rate limiting test (may take longer)
    print("\n" + "=" * 60)
    print("Running rate limiting test (this may take a moment)...")
    if test_rate_limiting():
        passed += 1
    total += 1
    
    print("\n" + "=" * 60)
    print("📊 AUTHENTICATION AND SECURITY TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All authentication and security tests passed!")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
    
    print("\n" + "=" * 60)
    print("🔐 Authentication and Security Tests Completed!")

if __name__ == "__main__":
    main() 