"""
Authentication API Routes
User registration, login, logout, password reset, and user management
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from database.database import get_db
from database.models import User
from auth.security import (
    verify_password, get_password_hash, create_tokens, refresh_access_token,
    Token, UserRole, validate_password_strength, AuthenticationError
)
from api.dependencies import (
    get_current_user, require_role, RequireRole, RequirePermission,
    get_pagination_params, PaginationParams, audit_log
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for requests/responses
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    role: str = Field(default=UserRole.EDITOR)

class AdminBootstrap(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    permissions: List[str]

    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class PasswordReset(BaseModel):
    email: EmailStr

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/bootstrap", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def bootstrap_admin_user(
    admin_data: AdminBootstrap,
    db: Session = Depends(get_db)
):
    """Bootstrap the first admin user (only works if no users exist)"""

    # Check if any users already exist
    existing_users = db.query(User).count()
    if existing_users > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bootstrap not allowed - users already exist. Use regular registration."
        )

    # Validate password confirmation
    if admin_data.password != admin_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    # Validate password strength
    if not validate_password_strength(admin_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )

    # Create the first admin user
    hashed_password = get_password_hash(admin_data.password)

    admin_user = User(
        email=admin_data.email,
        full_name=admin_data.full_name,
        hashed_password=hashed_password,
        role=UserRole.ADMIN,  # Force admin role for bootstrap
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    logger.info(f"Bootstrap admin user created: {admin_user.email}")

    return admin_user

@router.get("/bootstrap/status")
async def get_bootstrap_status(db: Session = Depends(get_db)):
    """Check if bootstrap is needed"""
    user_count = db.query(User).count()

    return {
        "bootstrap_needed": user_count == 0,
        "user_count": user_count,
        "message": "Bootstrap required - no users exist" if user_count == 0 else "System already initialized"
    }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = RequireRole.admin  # Only admins can create users
):
    """Register a new user (admin only)"""

    # Validate password strength
    if not validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )

    # Check if role is valid
    if user_data.role not in UserRole.get_all_roles():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(UserRole.get_all_roles())}"
        )

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {new_user.email} by admin {current_user.email}")

    return new_user

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """User login with email and password"""

    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        # Log failed login attempt
        logger.warning(f"Failed login attempt for email: {login_data.email} from IP: {request.client.host if request.client else 'unknown'}")
        raise AuthenticationError("Incorrect email or password")

    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    # Create tokens
    tokens = create_tokens(user.id, user.email, user.role)

    # Update last login (you might want to add this field to User model)
    # user.last_login = datetime.utcnow()
    # db.commit()

    logger.info(f"User logged in: {user.email}")

    return tokens

@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request,
    db: Session = Depends(get_db)
):
    """Login using OAuth2 password form (for compatibility)"""

    login_data = LoginRequest(email=form_data.username, password=form_data.password)
    return await login(login_data, request, db)

@router.post("/refresh", response_model=dict)
async def refresh_token(
    token_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""

    new_access_token = refresh_access_token(token_request.refresh_token)

    if not new_access_token:
        raise AuthenticationError("Invalid refresh token")

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    from auth.security import get_user_permissions

    permissions = get_user_permissions(current_user.role)

    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        permissions=permissions
    )

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("update", "user_profile"))
):
    """Update current user profile"""

    # Users can only update their own profile (not role)
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name

    if user_update.email is not None:
        # Check if email is already taken
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

        current_user.email = user_update.email

    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    logger.info(f"User profile updated: {current_user.email}")

    return current_user

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("change_password", "user"))
):
    """Change current user password"""

    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password strength
    if not validate_password_strength(password_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()

    logger.info(f"Password changed for user: {current_user.email}")

    return {"message": "Password changed successfully"}

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """User logout (client should discard tokens)"""

    # In a more sophisticated setup, you might maintain a blacklist of tokens
    # For now, just return success

    logger.info(f"User logged out: {current_user.email}")

    return {"message": "Logged out successfully"}

# Admin-only user management endpoints

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = RequirePermission.view_users,
    db: Session = Depends(get_db)
):
    """List all users (requires view_users permission)"""

    users = db.query(User).offset(pagination.skip).limit(pagination.limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = RequirePermission.view_users,
    db: Session = Depends(get_db)
):
    """Get specific user by ID"""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = RequirePermission.manage_users,
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("update", "user"))
):
    """Update user (admin only)"""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    if user_update.full_name is not None:
        user.full_name = user_update.full_name

    if user_update.email is not None:
        # Check if email is already taken
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != user_id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

        user.email = user_update.email

    if user_update.role is not None:
        if user_update.role not in UserRole.get_all_roles():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(UserRole.get_all_roles())}"
            )
        user.role = user_update.role

    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    logger.info(f"User updated: {user.email} by admin {current_user.email}")

    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = RequirePermission.manage_users,
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("delete", "user"))
):
    """Delete user (admin only)"""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Instead of hard delete, deactivate the user
    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()

    logger.info(f"User deactivated: {user.email} by admin {current_user.email}")

    return {"message": "User deactivated successfully"}

@router.post("/users/{user_id}/reset-password")
async def admin_reset_password(
    user_id: int,
    current_user: User = RequirePermission.manage_users,
    db: Session = Depends(get_db),
    _audit: dict = Depends(audit_log("reset_password", "user"))
):
    """Reset user password (admin only) - generates temporary password"""
    import secrets
    import string

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate temporary password
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%") for _ in range(12))

    # Update user password
    user.hashed_password = get_password_hash(temp_password)
    user.updated_at = datetime.utcnow()
    db.commit()

    logger.info(f"Password reset for user: {user.email} by admin {current_user.email}")

    # In production, you would send this via email instead of returning it
    return {
        "message": "Password reset successfully",
        "temporary_password": temp_password,
        "note": "User should change this password on first login"
    }

@router.get("/roles", response_model=List[str])
async def get_available_roles(
    current_user: User = RequirePermission.view_users
):
    """Get list of available user roles"""
    return UserRole.get_all_roles()

@router.get("/permissions", response_model=List[str])
async def get_user_permissions_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Get current user's permissions"""
    from auth.security import get_user_permissions
    return get_user_permissions(current_user.role)

@router.post("/password-reset-request")
async def request_password_reset(
    reset_request: PasswordReset,
    db: Session = Depends(get_db)
):
    """Request password reset (would send email in production)"""

    user = db.query(User).filter(User.email == reset_request.email).first()

    # Always return success to prevent email enumeration
    # In production, send reset email only if user exists

    if user:
        # Generate reset token (in production, store this in database with expiration)
        # Send email with reset link
        logger.info(f"Password reset requested for: {user.email}")

    return {"message": "If the email exists, a password reset link will be sent"}

@router.get("/stats")
async def get_user_stats(
    current_user: User = RequirePermission.view_users,
    db: Session = Depends(get_db)
):
    """Get user statistics"""

    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()

    # Count by role
    role_counts = {}
    for role in UserRole.get_all_roles():
        count = db.query(User).filter(User.role == role, User.is_active == True).count()
        role_counts[role] = count

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "role_distribution": role_counts
    }
