"""
Middleware Module
Handles rate limiting, request logging, security headers, and other middleware functionality.
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from collections import defaultdict
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os

from .auth import get_optional_user, User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting implementation."""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests: Dict[str, List[float]] = defaultdict(list)
        self.hour_requests: Dict[str, List[float]] = defaultdict(list)
    
    def _cleanup_old_requests(self, key: str):
        """Remove old requests outside the time window."""
        now = time.time()
        
        # Clean up minute requests (older than 60 seconds)
        self.minute_requests[key] = [
            req_time for req_time in self.minute_requests[key]
            if now - req_time < 60
        ]
        
        # Clean up hour requests (older than 3600 seconds)
        self.hour_requests[key] = [
            req_time for req_time in self.hour_requests[key]
            if now - req_time < 3600
        ]
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed based on rate limits."""
        self._cleanup_old_requests(key)
        now = time.time()
        
        # Check minute limit
        if len(self.minute_requests[key]) >= self.requests_per_minute:
            return False
        
        # Check hour limit
        if len(self.hour_requests[key]) >= self.requests_per_hour:
            return False
        
        # Add current request
        self.minute_requests[key].append(now)
        self.hour_requests[key].append(now)
        
        return True
    
    def get_remaining_requests(self, key: str) -> Dict[str, int]:
        """Get remaining requests for a key."""
        self._cleanup_old_requests(key)
        
        return {
            "minute": max(0, self.requests_per_minute - len(self.minute_requests[key])),
            "hour": max(0, self.requests_per_hour - len(self.hour_requests[key]))
        }

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for adding security headers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client identifier (IP or user ID)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not self.rate_limiter.is_allowed(client_id):
            remaining = self.rate_limiter.get_remaining_requests(client_id)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": 60,
                    "remaining": remaining
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Remaining-Minute": str(remaining["minute"]),
                    "X-RateLimit-Remaining-Hour": str(remaining["hour"])
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.rate_limiter.get_remaining_requests(client_id)
        response.headers["X-RateLimit-Remaining-Minute"] = str(remaining["minute"])
        response.headers["X-RateLimit-Remaining-Hour"] = str(remaining["hour"])
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get user ID if authenticated
        try:
            user = get_optional_user(request)
            if user:
                return f"user:{user.user_id}"
        except:
            pass
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        return f"ip:{request.client.host}"

class LoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path} - Client: {request.client.host}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class CORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware with configurable origins."""
    
    def __init__(self, app, allowed_origins: List[str] = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Handle CORS
        origin = request.headers.get("Origin")
        if origin and (origin in self.allowed_origins or "*" in self.allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
        
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Error handling middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            
            # Return generic error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred"
                }
            )

# Global rate limiter instance
rate_limiter = RateLimiter(
    requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
    requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
)

def setup_middleware(app):
    """Setup all middleware for the FastAPI app."""
    # Add middleware in order (last added is executed first)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allowed_origins=os.getenv("ALLOWED_ORIGINS", "*").split(",")
    ) 