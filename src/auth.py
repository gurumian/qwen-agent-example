"""
Authentication and Authorization Module
Handles API key validation, JWT tokens, and role-based access control.
"""

import os
import time
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from .config import Config

# Security scheme
security = HTTPBearer()

class User(BaseModel):
    """User model for authentication."""
    user_id: str
    username: str
    email: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class APIKey(BaseModel):
    """API key model."""
    key_id: str
    key_hash: str
    user_id: str
    name: str
    permissions: List[str]
    is_active: bool = True
    created_at: datetime
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class AuthManager:
    """Manages authentication and authorization."""
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # In-memory storage (replace with database in production)
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default admin user
        self._init_default_admin()
    
    def _init_default_admin(self):
        """Initialize default admin user."""
        admin_user = User(
            user_id="admin",
            username="admin",
            email="admin@example.com",
            roles=["admin"],
            permissions=["*"],
            created_at=datetime.utcnow()
        )
        self.users["admin"] = admin_user
        
        # Create default API key for admin
        default_api_key = self.create_api_key(
            user_id="admin",
            name="Default Admin Key",
            permissions=["*"]
        )
        print(f"🔑 Default admin API key created successfully")
    
    def create_user(self, username: str, email: str, roles: List[str] = None) -> User:
        """Create a new user."""
        user_id = secrets.token_urlsafe(16)
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            roles=roles or ["user"],
            permissions=self._get_permissions_for_roles(roles or ["user"]),
            created_at=datetime.utcnow()
        )
        self.users[user_id] = user
        return user
    
    def create_api_key(self, user_id: str, name: str, permissions: List[str] = None) -> str:
        """Create a new API key for a user."""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        # Generate API key
        api_key = secrets.token_urlsafe(32)
        key_id = secrets.token_urlsafe(16)
        
        # Hash the API key for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Store API key info
        api_key_info = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            user_id=user_id,
            name=name,
            permissions=permissions or self.users[user_id].permissions,
            created_at=datetime.utcnow()
        )
        self.api_keys[key_id] = api_key_info
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[User]:
        """Validate an API key and return the associated user."""
        if not api_key:
            return None
        
        # Hash the provided API key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Find matching API key
        for key_info in self.api_keys.values():
            if key_info.key_hash == key_hash and key_info.is_active:
                # Check if key is expired
                if key_info.expires_at and datetime.utcnow() > key_info.expires_at:
                    continue
                
                # Update last used timestamp
                key_info.last_used = datetime.utcnow()
                
                # Return associated user
                return self.users.get(key_info.user_id)
        
        return None
    
    def create_access_token(self, user: User) -> str:
        """Create a JWT access token for a user."""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode = {
            "sub": user.user_id,
            "username": user.username,
            "roles": user.roles,
            "permissions": user.permissions,
            "exp": expire
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT access token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def _get_permissions_for_roles(self, roles: List[str]) -> List[str]:
        """Get permissions for given roles."""
        role_permissions = {
            "admin": ["*"],
            "user": ["chat", "read", "upload"],
            "moderator": ["chat", "read", "upload", "moderate"],
            "developer": ["chat", "read", "upload", "admin:read"]
        }
        
        permissions = []
        for role in roles:
            if role in role_permissions:
                permissions.extend(role_permissions[role])
        
        return list(set(permissions))  # Remove duplicates
    
    def has_permission(self, user: User, permission: str) -> bool:
        """Check if user has a specific permission."""
        if "*" in user.permissions:
            return True
        return permission in user.permissions
    
    def require_permission(self, permission: str):
        """Decorator to require a specific permission."""
        def permission_checker(user: User = Depends(get_current_user)):
            if not self.has_permission(user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission}"
                )
            return user
        return permission_checker

# Global auth manager instance
auth_manager = AuthManager()

def get_current_user_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from API key."""
    api_key = credentials.credentials
    
    # Try API key first
    user = auth_manager.validate_api_key(api_key)
    if user:
        return user
    
    # Try JWT token
    payload = auth_manager.decode_access_token(api_key)
    if payload:
        user_id = payload.get("sub")
        if user_id and user_id in auth_manager.users:
            return auth_manager.users[user_id]
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key or token",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token."""
    token = credentials.credentials
    payload = auth_manager.decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None or user_id not in auth_manager.users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return auth_manager.users[user_id]

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    try:
        return get_current_user_api_key(credentials)
    except HTTPException:
        return None

# Permission decorators
def require_auth():
    """Require authentication."""
    return get_current_user_api_key

def require_permission(permission: str):
    """Require a specific permission."""
    return auth_manager.require_permission(permission)

def require_admin():
    """Require admin role."""
    def admin_checker(user: User = Depends(get_current_user_api_key)):
        if "admin" not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return user
    return admin_checker 