"""
Authentication Middleware
"""

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, Dict
import jwt
import os
from datetime import datetime, timedelta

security = HTTPBearer()

class AuthMiddleware(BaseHTTPMiddleware):
    """JWT-based authentication middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.secret_key = os.getenv("JWT_SECRET_KEY", "netintel-ocr-secret-key")
        self.algorithm = "HS256"
        self.exempt_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/api/v1/health"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Check for authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return HTTPException(status_code=401, detail="Missing authentication token")
        
        # Validate token
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            request.state.user = payload
        except jwt.ExpiredSignatureError:
            return HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            return HTTPException(status_code=401, detail="Invalid token")
        
        response = await call_next(request)
        return response

async def get_current_user(credentials: HTTPAuthorizationCredentials = security) -> Dict:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    secret_key = os.getenv("JWT_SECRET_KEY", "netintel-ocr-secret-key")
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def require_admin(user: Dict = get_current_user) -> Dict:
    """Require admin role for access"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token"""
    secret_key = os.getenv("JWT_SECRET_KEY", "netintel-ocr-secret-key")
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt