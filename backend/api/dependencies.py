"""
API Dependencies
Authentication, authorization, and database dependencies for FastAPI
"""

import logging
from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models import User
from auth.security import verify_token, TokenData, has_permission, AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)

# Security scheme for JWT
security = HTTPBearer()

def get_db() -> Generator[Session, None, None]:
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """Extract and verify JWT token"""
    token = credentials.credentials

    token_data = verify_token(token)
    if token_data is None:
        raise AuthenticationError("Invalid authentication credentials")

    return token_data

async def get_current_user(
    token_data: TokenData = Depends(get_current_user_token),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    user = db.query(User).filter(User.id == token_data.user_id).first()

    if user is None:
        raise AuthenticationError("User not found")

    if not user.is_active:
        raise AuthenticationError("User account is disabled")

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (alias for clarity)"""
    return current_user

def require_permission(permission: str):
    """Dependency factory for permission-based authorization"""
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not has_permission(current_user.role, permission):
            raise AuthorizationError(f"Permission '{permission}' required")
        return current_user

    return permission_checker

def require_role(required_role: str):
    """Dependency factory for role-based authorization"""
    from auth.security import has_role_level

    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not has_role_level(current_user.role, required_role):
            raise AuthorizationError(f"Role '{required_role}' or higher required")
        return current_user

    return role_checker

# Pre-built permission dependencies
class RequirePermission:
    """Pre-built permission dependencies"""

    create_content = Depends(require_permission("create_content"))
    edit_content = Depends(require_permission("edit_content"))
    delete_content = Depends(require_permission("delete_content"))
    approve_content = Depends(require_permission("approve_content"))
    publish_content = Depends(require_permission("publish_content"))

    manage_brands = Depends(require_permission("manage_brands"))
    view_brands = Depends(require_permission("view_brands"))

    manage_users = Depends(require_permission("manage_users"))
    view_users = Depends(require_permission("view_users"))

    view_analytics = Depends(require_permission("view_analytics"))
    export_analytics = Depends(require_permission("export_analytics"))

    manage_settings = Depends(require_permission("manage_settings"))
    view_logs = Depends(require_permission("view_logs"))

# Pre-built role dependencies
class RequireRole:
    """Pre-built role dependencies"""

    admin = Depends(require_role("admin"))
    manager = Depends(require_role("manager"))
    editor = Depends(require_role("editor"))
    viewer = Depends(require_role("viewer"))

async def get_optional_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    try:
        # Try to get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]
        token_data = verify_token(token)

        if token_data is None:
            return None

        user = db.query(User).filter(User.id == token_data.user_id).first()

        if user and user.is_active:
            return user

        return None

    except Exception:
        return None

def get_brand_access_filter(current_user: User):
    """Get brand access filter based on user role"""
    from auth.security import UserRole

    # Admins and managers can access all brands
    if current_user.role in [UserRole.ADMIN, UserRole.MANAGER]:
        return None  # No filter needed

    # Other roles can only access brands they own
    from database.models import Brand
    return Brand.owner_id == current_user.id

def get_user_brands(current_user: User, db: Session):
    """Get brands accessible to current user"""
    from database.models import Brand
    from auth.security import UserRole

    query = db.query(Brand)

    # Apply access filter
    brand_filter = get_brand_access_filter(current_user)
    if brand_filter is not None:
        query = query.filter(brand_filter)

    return query.all()

async def verify_brand_access(
    brand_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify user has access to specific brand"""
    from database.models import Brand

    brand = db.query(Brand).filter(Brand.id == brand_id).first()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )

    # Check access
    brand_filter = get_brand_access_filter(current_user)
    if brand_filter is not None:
        # User has restricted access, check if they own this brand
        if brand.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this brand"
            )

    return brand

class RateLimitDependency:
    """Rate limiting dependency"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def __call__(
        self,
        request: Request,
        current_user: User = Depends(get_current_user)
    ):
        # This would integrate with Redis for rate limiting
        # For now, just pass through
        return True

def rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    """Rate limiting dependency factory"""
    return RateLimitDependency(max_requests, window_seconds)

class AuditLogDependency:
    """Audit logging dependency"""

    def __init__(self, action: str, resource: str):
        self.action = action
        self.resource = resource

    async def __call__(
        self,
        request: Request,
        current_user: User = Depends(get_current_user)
    ):
        # Log the action
        from auth.security import audit_log_entry

        log_entry = audit_log_entry(
            user_id=current_user.id,
            action=self.action,
            resource=self.resource,
            details={
                "method": request.method,
                "url": str(request.url),
                "user_agent": request.headers.get("user-agent"),
                "ip_address": request.client.host if request.client else None
            }
        )

        # In production, this would be sent to a logging service
        logger.info(f"Audit log: {log_entry}")

        return log_entry

def audit_log(action: str, resource: str):
    """Audit logging dependency factory"""
    return AuditLogDependency(action, resource)

async def validate_content_ownership(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate user has access to specific content"""
    from database.models import ContentPost
    from auth.security import UserRole

    content = db.query(ContentPost).filter(ContentPost.id == content_id).first()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    # Admins and managers can access all content
    if current_user.role in [UserRole.ADMIN, UserRole.MANAGER]:
        return content

    # Check if user owns the brand that owns this content
    if content.brand.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this content"
        )

    return content

class PaginationParams:
    """Pagination parameters"""

    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        max_limit: int = 1000
    ):
        self.skip = skip
        self.limit = min(limit, max_limit)

def get_pagination_params(
    skip: int = 0,
    limit: int = 100
) -> PaginationParams:
    """Get pagination parameters with validation"""
    return PaginationParams(skip=skip, limit=limit)

class FilterParams:
    """Common filter parameters"""

    def __init__(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None,
        platform: Optional[str] = None
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.platform = platform

def get_filter_params(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    platform: Optional[str] = None
) -> FilterParams:
    """Get filter parameters"""
    return FilterParams(
        start_date=start_date,
        end_date=end_date,
        status=status,
        platform=platform
    )

async def validate_api_key(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Validate API key for external integrations"""
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return None

    from auth.security import verify_api_key

    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format"
        )

    # In production, you'd look up the API key in the database
    # For now, just return None to indicate no user associated
    return None

class WebhookValidation:
    """Webhook signature validation"""

    def __init__(self, secret_header: str = "X-Webhook-Secret"):
        self.secret_header = secret_header

    async def __call__(self, request: Request):
        import hmac
        import hashlib
        from config.settings import get_settings

        settings = get_settings()
        provided_secret = request.headers.get(self.secret_header)

        if not provided_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Webhook secret required"
            )

        # Get request body
        body = await request.body()

        # Calculate expected signature
        expected_signature = hmac.new(
            settings.webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        # Compare signatures
        if not hmac.compare_digest(provided_secret, expected_signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )

        return True

def validate_webhook_signature():
    """Webhook signature validation dependency"""
    return WebhookValidation()
