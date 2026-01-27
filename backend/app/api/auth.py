"""
Authentication API Routes

Provides endpoints for:
- User registration
- User login
- Token refresh
- Logout
- Password reset
- Profile management
"""

from datetime import datetime, timedelta
from typing import Annotated
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.settings_model import UserSettings
from app.models.workspace import Workspace
from app.models.refresh_token import RefreshToken
from app.models.activity import Activity
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    TokenRefreshRequest,
    AccessTokenResponse,
    PasswordChangeRequest,
)
from app.schemas.common import MessageResponse
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_token,
)
from app.api.deps import CurrentUser, DatabaseSession
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def create_default_workspaces(db: Session, user_id: str) -> None:
    """Create default workspaces for a new user."""
    default_workspaces = [
        {"name": "Sales Analytics", "description": "Sales performance and analysis", "color": "blue"},
        {"name": "Marketing", "description": "Marketing campaigns and metrics", "color": "purple"},
        {"name": "Financial", "description": "Financial reports and analysis", "color": "green"},
    ]
    
    for ws_data in default_workspaces:
        workspace = Workspace(
            user_id=user_id,
            name=ws_data["name"],
            description=ws_data["description"],
            color=ws_data["color"],
        )
        db.add(workspace)


def create_default_settings(db: Session, user_id: str) -> None:
    """Create default settings for a new user."""
    user_settings = UserSettings(user_id=user_id)
    db.add(user_settings)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: DatabaseSession,
):
    """
    Register a new user account.
    
    Creates the user, default settings, default workspaces,
    and returns authentication tokens.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(user)
    db.flush()  # Get the user ID
    
    # Create default settings and workspaces
    create_default_settings(db, user.id)
    create_default_workspaces(db, user.id)
    
    # Log registration activity
    activity = Activity(
        user_id=user.id,
        activity_type="registration",
        title="Account created",
        status="success",
    )
    db.add(activity)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token, token_hash, expires_at = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token
    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(refresh_token_record)
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"New user registered: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user.to_dict()),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: DatabaseSession,
):
    """
    Authenticate user and return tokens.
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token, token_hash, expires_at = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token
    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(refresh_token_record)
    
    # Log login activity
    activity = Activity(
        user_id=user.id,
        activity_type="login",
        title="User logged in",
        status="success",
    )
    db.add(activity)
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"User logged in: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user.to_dict()),
    )


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: DatabaseSession,
):
    """
    Refresh access token using refresh token.
    """
    # Verify refresh token
    payload = verify_token(refresh_data.refresh_token, token_type="refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Verify token exists in database and is not revoked
    token_hash = hash_token(refresh_data.refresh_token)
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked == False,
    ).first()
    
    if not stored_token or not stored_token.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or revoked"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new access token
    new_access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    return AccessTokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: CurrentUser,
    refresh_data: TokenRefreshRequest,
    db: DatabaseSession,
):
    """
    Logout user by revoking refresh token.
    """
    # Revoke the provided refresh token
    token_hash = hash_token(refresh_data.refresh_token)
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.user_id == current_user.id,
    ).first()
    
    if stored_token:
        stored_token.revoke()
    
    # Log logout activity
    activity = Activity(
        user_id=current_user.id,
        activity_type="logout",
        title="User logged out",
        status="success",
    )
    db.add(activity)
    
    db.commit()
    
    logger.info(f"User logged out: {current_user.email}")
    
    return MessageResponse(message="Successfully logged out")


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: CurrentUser):
    """
    Get current user's profile.
    """
    return UserResponse.model_validate(current_user.to_dict())


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    current_user: CurrentUser,
    db: DatabaseSession,
    full_name: str = None,
):
    """
    Update current user's profile.
    """
    if full_name:
        current_user.full_name = full_name.strip()
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user.to_dict())


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    current_user: CurrentUser,
    password_data: PasswordChangeRequest,
    db: DatabaseSession,
):
    """
    Change current user's password.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    
    # Revoke all refresh tokens (force re-login)
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked == False,
    ).update({"revoked": True, "revoked_at": datetime.utcnow()})
    
    db.commit()
    
    logger.info(f"Password changed for user: {current_user.email}")
    
    return MessageResponse(message="Password changed successfully. Please login again.")
