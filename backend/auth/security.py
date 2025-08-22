"""
Authentication and Security Module
JWT token management, password hashing, and role-based access control
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None

class UserRole:
    ADMIN = "admin"
    MANAGER = "manager"
    EDITOR = "editor"
    VIEWER = "viewer"

    @classmethod
    def get_all_roles(cls) -> List[str]:
        return [cls.ADMIN, cls.MANAGER, cls.EDITOR, cls.VIEWER]

    @classmethod
    def get_role_hierarchy(cls) -> Dict[str, int]:
        """Role hierarchy for permission checking (higher number = more permissions)"""
        return {
            cls.VIEWER: 1,
            cls.EDITOR: 2,
            cls.MANAGER: 3,
            cls.ADMIN: 4
        }

class Permission:
    # Content permissions
    CREATE_CONTENT = "create_content"
    EDIT_CONTENT = "edit_content"
    DELETE_CONTENT = "delete_content"
    APPROVE_CONTENT = "approve_content"
    PUBLISH_CONTENT = "publish_content"

    # Brand permissions
    MANAGE_BRANDS = "manage_brands"
    VIEW_BRANDS = "view_brands"

    # User permissions
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"

    # Analytics permissions
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_ANALYTICS = "export_analytics"

    # System permissions
    MANAGE_SETTINGS = "manage_settings"
    VIEW_LOGS = "view_logs"

# Role-based permissions mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT,
        Permission.DELETE_CONTENT,
        Permission.APPROVE_CONTENT,
        Permission.PUBLISH_CONTENT,
        Permission.MANAGE_BRANDS,
        Permission.VIEW_BRANDS,
        Permission.MANAGE_USERS,
        Permission.VIEW_USERS,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_ANALYTICS,
        Permission.MANAGE_SETTINGS,
        Permission.VIEW_LOGS,
    ],
    UserRole.MANAGER: [
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT,
        Permission.DELETE_CONTENT,
        Permission.APPROVE_CONTENT,
        Permission.PUBLISH_CONTENT,
        Permission.MANAGE_BRANDS,
        Permission.VIEW_BRANDS,
        Permission.VIEW_USERS,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_ANALYTICS,
    ],
    UserRole.EDITOR: [
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT,
        Permission.VIEW_BRANDS,
        Permission.VIEW_ANALYTICS,
    ],
    UserRole.VIEWER: [
        Permission.VIEW_BRANDS,
        Permission.VIEW_ANALYTICS,
    ],
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token(data: Dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        # Verify token type
        if payload.get("type") != token_type:
            return None

        user_id: int = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")

        if user_id is None:
            return None

        return TokenData(user_id=user_id, email=email, role=role)

    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None

def create_tokens(user_id: int, email: str, role: str) -> Token:
    """Create both access and refresh tokens"""
    token_data = {
        "sub": user_id,
        "email": email,
        "role": role
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )

def refresh_access_token(refresh_token: str) -> Optional[str]:
    """Create new access token from refresh token"""
    token_data = verify_token(refresh_token, token_type="refresh")

    if not token_data:
        return None

    new_access_token = create_access_token({
        "sub": token_data.user_id,
        "email": token_data.email,
        "role": token_data.role
    })

    return new_access_token

def has_permission(user_role: str, required_permission: str) -> bool:
    """Check if user role has required permission"""
    if user_role not in ROLE_PERMISSIONS:
        return False

    return required_permission in ROLE_PERMISSIONS[user_role]

def has_role_level(user_role: str, required_role: str) -> bool:
    """Check if user has at least the required role level"""
    hierarchy = UserRole.get_role_hierarchy()

    user_level = hierarchy.get(user_role, 0)
    required_level = hierarchy.get(required_role, 0)

    return user_level >= required_level

def get_user_permissions(user_role: str) -> List[str]:
    """Get all permissions for a user role"""
    return ROLE_PERMISSIONS.get(user_role, [])

class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

def validate_password_strength(password: str) -> bool:
    """Validate password meets security requirements"""
    if len(password) < 8:
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    return has_upper and has_lower and has_digit and has_special

def generate_api_key(user_id: int, purpose: str = "general") -> str:
    """Generate API key for external integrations"""
    import secrets
    import hashlib

    # Create a unique API key
    random_part = secrets.token_urlsafe(32)
    user_part = f"{user_id}_{purpose}"

    # Create hash for verification
    api_key = f"asm_{hashlib.sha256(f'{user_part}_{random_part}'.encode()).hexdigest()[:32]}"

    return api_key

def verify_api_key(api_key: str) -> bool:
    """Verify API key format and structure"""
    if not api_key.startswith("asm_"):
        return False

    if len(api_key) != 36:  # asm_ + 32 chars
        return False

    return True

class SecurityHeaders:
    """Security headers for API responses"""

    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
        }

def sanitize_input(input_string: str) -> str:
    """Basic input sanitization"""
    import html
    import re

    # HTML escape
    sanitized = html.escape(input_string)

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', sanitized)

    return sanitized.strip()

def rate_limit_key(user_id: int, endpoint: str) -> str:
    """Generate rate limit key for Redis"""
    return f"rate_limit:{user_id}:{endpoint}"

def audit_log_entry(user_id: int, action: str, resource: str, details: Dict = None) -> Dict:
    """Create audit log entry"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "details": details or {},
        "ip_address": None,  # Should be filled by middleware
        "user_agent": None,  # Should be filled by middleware
    }
