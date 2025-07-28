"""
API Security Module
Simple security features for the chatbot API.
"""

import time
import os
from collections import defaultdict
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests = defaultdict(list)
        self.hour_requests = defaultdict(list)
    
    def _cleanup_old_requests(self, key: str):
        """Remove old requests from tracking."""
        current_time = time.time()
        
        # Clean minute requests (older than 60 seconds)
        self.minute_requests[key] = [
            req_time for req_time in self.minute_requests[key]
            if current_time - req_time < 60
        ]
        
        # Clean hour requests (older than 3600 seconds)
        self.hour_requests[key] = [
            req_time for req_time in self.hour_requests[key]
            if current_time - req_time < 3600
        ]
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed based on rate limits."""
        self._cleanup_old_requests(key)
        current_time = time.time()
        
        # Check minute limit
        if len(self.minute_requests[key]) >= self.requests_per_minute:
            return False
        
        # Check hour limit
        if len(self.hour_requests[key]) >= self.requests_per_hour:
            return False
        
        # Add current request
        self.minute_requests[key].append(current_time)
        self.hour_requests[key].append(current_time)
        
        return True
    
    def get_remaining_requests(self, key: str) -> Dict[str, int]:
        """Get remaining requests for a key."""
        self._cleanup_old_requests(key)
        
        return {
            "minute": max(0, self.requests_per_minute - len(self.minute_requests[key])),
            "hour": max(0, self.requests_per_hour - len(self.hour_requests[key]))
        }


class APISecurity:
    """API security manager."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter(
            requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
            requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
        )
        self.allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    def get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Use IP address as client identifier
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        return f"ip:{request.client.host}"
    
    def check_rate_limit(self, request: Request) -> bool:
        """Check if request is within rate limits."""
        client_id = self.get_client_id(request)
        return self.rate_limiter.is_allowed(client_id)
    
    def get_rate_limit_headers(self, request: Request) -> Dict[str, str]:
        """Get rate limit headers for response."""
        client_id = self.get_client_id(request)
        remaining = self.rate_limiter.get_remaining_requests(client_id)
        
        return {
            "X-RateLimit-Limit-Minute": str(self.rate_limiter.requests_per_minute),
            "X-RateLimit-Limit-Hour": str(self.rate_limiter.requests_per_hour),
            "X-RateLimit-Remaining-Minute": str(remaining["minute"]),
            "X-RateLimit-Remaining-Hour": str(remaining["hour"])
        }
    
    def validate_request_size(self, request: Request) -> bool:
        """Validate request size to prevent abuse."""
        content_length = request.headers.get("content-length")
        if content_length:
            size_mb = int(content_length) / (1024 * 1024)
            if size_mb > 10:  # 10MB limit
                return False
        return True
    
    def add_security_headers(self, response: JSONResponse) -> JSONResponse:
        """Add security headers to response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


# Global security instance
api_security = APISecurity()


def require_rate_limit(request: Request):
    """Dependency to enforce rate limiting."""
    if not api_security.check_rate_limit(request):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    if not api_security.validate_request_size(request):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Request too large. Maximum size is 10MB."
        ) 