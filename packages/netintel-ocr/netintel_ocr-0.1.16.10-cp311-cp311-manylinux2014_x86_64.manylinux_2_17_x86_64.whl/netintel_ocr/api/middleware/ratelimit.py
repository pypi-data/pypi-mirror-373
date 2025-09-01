"""
Rate Limiting Middleware
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
import os

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm"""
    
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()
        
        # Configuration from environment
        self.window_seconds = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        self.max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
        self.enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        
        # Get client identifier (IP address or user ID)
        client_id = request.client.host if request.client else "unknown"
        if hasattr(request.state, "user") and request.state.user:
            client_id = request.state.user.get("id", client_id)
        
        # Check rate limit
        async with self.lock:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=self.window_seconds)
            
            # Clean old requests
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > window_start
            ]
            
            # Check if limit exceeded
            if len(self.requests[client_id]) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds} seconds"
                )
            
            # Add current request
            self.requests[client_id].append(now)
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            self.max_requests - len(self.requests[client_id])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int((now + timedelta(seconds=self.window_seconds)).timestamp())
        )
        
        return response