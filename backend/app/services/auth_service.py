"""
Authentication Service

Business logic for user authentication and authorization.
"""

from typing import Optional
from datetime import datetime
import logging

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_token,
)
from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        is_admin: bool = False,
    ) -> User:
        """
        Create a new user.
        
        Args:
            email: User email address
            password: Plain text password (will be hashed)
            full_name: User's display name
            is_admin: Admin role flag
            
        Returns:
            Created User object
            
        Raises:
            ConflictError: If email already exists
        """
        # Check for existing user
        existing = self.get_user_by_email(email)
        if existing:
            raise ConflictError(
                message="Email already registered",
                code="AUTH_005",
            )
        
        # Create user
        user = User(
            email=email,
            password_hash=get_password_hash(password),
            full_name=full_name,
            is_admin=is_admin,
        )
        self.db.add(user)
        self.db.flush()  # Get the ID without committing
        
        logger.info(f"Created new user: {email}")
        return user
    
    def authenticate_user(self, email: str, password: str) -> User:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            Authenticated User object
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        user = self.get_user_by_email(email)
        
        if not user:
            raise AuthenticationError(
                message="Invalid email or password",
                code="AUTH_001",
            )
        
        if not verify_password(password, user.password_hash):
            raise AuthenticationError(
                message="Invalid email or password",
                code="AUTH_001",
            )
        
        if not user.is_active:
            raise AuthenticationError(
                message="Account is inactive",
                code="AUTH_001",
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        logger.info(f"User authenticated: {email}")
        return user
    
    def create_tokens(self, user: User) -> tuple[str, str, datetime]:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user: User to create tokens for
            
        Returns:
            Tuple of (access_token, refresh_token, refresh_expires_at)
        """
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # Create refresh token
        refresh_token, token_hash, expires_at = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        # Store refresh token in database
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(refresh_token_record)
        
        return access_token, refresh_token, expires_at
    
    def refresh_access_token(self, refresh_token: str) -> tuple[str, User]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Tuple of (new_access_token, user)
            
        Raises:
            AuthenticationError: If refresh token is invalid
        """
        # Verify token
        payload = verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise AuthenticationError(
                message="Invalid or expired refresh token",
                code="AUTH_002",
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError(
                message="Invalid token payload",
                code="AUTH_003",
            )
        
        # Verify token exists in database
        token_hash = hash_token(refresh_token)
        stored_token = self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
        ).first()
        
        if not stored_token or not stored_token.is_valid:
            raise AuthenticationError(
                message="Refresh token is invalid or revoked",
                code="AUTH_003",
            )
        
        # Get user
        user = self.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError(
                message="User not found or inactive",
                code="AUTH_001",
            )
        
        # Create new access token
        new_access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return new_access_token, user
    
    def revoke_refresh_token(self, refresh_token: str, user_id: str) -> bool:
        """
        Revoke a refresh token.
        
        Args:
            refresh_token: Token to revoke
            user_id: Owner user ID
            
        Returns:
            True if token was revoked, False if not found
        """
        token_hash = hash_token(refresh_token)
        stored_token = self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == user_id,
        ).first()
        
        if stored_token:
            stored_token.revoke()
            return True
        
        return False
    
    def revoke_all_refresh_tokens(self, user_id: str) -> int:
        """
        Revoke all refresh tokens for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of tokens revoked
        """
        result = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False,
        ).update({
            "revoked": True,
            "revoked_at": datetime.utcnow(),
        })
        
        return result
    
    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        """
        Change user password.
        
        Args:
            user: User to change password for
            current_password: Current password
            new_password: New password
            
        Raises:
            AuthenticationError: If current password is incorrect
        """
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationError(
                message="Current password is incorrect",
                code="AUTH_001",
            )
        
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        # Revoke all refresh tokens
        self.revoke_all_refresh_tokens(str(user.id))
        
        logger.info(f"Password changed for user: {user.email}")
    
    def cleanup_expired_tokens(self) -> int:
        """
        Remove expired refresh tokens from database.
        
        Returns:
            Number of tokens removed
        """
        result = self.db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ).delete()
        
        logger.info(f"Cleaned up {result} expired refresh tokens")
        return result
