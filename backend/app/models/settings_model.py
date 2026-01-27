"""
Settings Model

Defines the UserSettings and ApiKey entities.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, Text, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class UserSettings(Base):
    """
    UserSettings model for user preferences.
    
    Attributes:
        user_id: User ID (primary key, foreign key)
        theme: UI theme (dark, light, system)
        language: Preferred language code
        notifications_enabled: Enable in-app notifications
        auto_refresh: Enable auto-refresh for dashboard
        refresh_interval: Refresh interval in seconds
        default_chart_type: Default chart type for visualizations
        timezone: User's timezone
        preferences: Additional preferences (JSONB)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "settings"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    theme = Column(String(50), default="dark", nullable=False)
    language = Column(String(50), default="en", nullable=False)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    auto_refresh = Column(Boolean, default=True, nullable=False)
    refresh_interval = Column(Integer, default=60, nullable=False)
    default_chart_type = Column(String(50), default="bar", nullable=False)
    timezone = Column(String(100), default="UTC", nullable=False)
    preferences = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="settings")
    
    def __repr__(self) -> str:
        return f"<UserSettings(user_id={self.user_id})>"
    
    def to_dict(self, include_api_keys: bool = False, api_keys: list = None) -> dict:
        """Convert settings to dictionary."""
        result = {
            "theme": self.theme,
            "language": self.language,
            "notifications_enabled": self.notifications_enabled,
            "auto_refresh": self.auto_refresh,
            "refresh_interval": self.refresh_interval,
            "default_chart_type": self.default_chart_type,
            "timezone": self.timezone,
            "preferences": self.preferences or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_api_keys and api_keys is not None:
            result["api_keys"] = {key.key_name: key.masked_value for key in api_keys}
        
        return result


class ApiKey(Base):
    """
    ApiKey model for storing encrypted API keys.
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: Owner user ID
        key_name: Name/identifier for the key
        key_value_encrypted: Encrypted key value
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    key_name = Column(String(255), nullable=False)
    key_value_encrypted = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "key_name", name="uq_user_key_name"),
        Index("idx_api_keys_user_id", "user_id"),
    )
    
    def __repr__(self) -> str:
        return f"<ApiKey(id={self.id}, name='{self.key_name}')>"
    
    @property
    def masked_value(self) -> str:
        """Return masked key value for display."""
        # This is a placeholder - actual value would need decryption first
        return "****" + "****"
    
    def to_dict(self) -> dict:
        """Convert API key to dictionary (masked)."""
        return {
            "id": str(self.id),
            "key_name": self.key_name,
            "key_value": self.masked_value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
