"""
RefreshToken Model

Defines the RefreshToken entity for JWT refresh token management.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class RefreshToken(Base):
    """
    RefreshToken model for managing JWT refresh tokens.
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: Owner user ID
        token_hash: Hashed token value (for security)
        expires_at: Token expiration timestamp
        created_at: Creation timestamp
        revoked: Whether token has been revoked
        revoked_at: Revocation timestamp
    """
    
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    # Indexes
    __table_args__ = (
        Index("idx_refresh_tokens_user_id", "user_id"),
        Index("idx_refresh_tokens_token_hash", "token_hash"),
        Index("idx_refresh_tokens_expires_at", "expires_at"),
    )
    
    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"
    
    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not revoked)."""
        return not self.revoked and self.expires_at > datetime.utcnow()
    
    def revoke(self) -> None:
        """Revoke this refresh token."""
        self.revoked = True
        self.revoked_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert refresh token to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "revoked": self.revoked,
            "is_valid": self.is_valid,
        }
