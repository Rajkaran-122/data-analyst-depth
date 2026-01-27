"""
Activity Model

Defines the Activity entity for tracking user actions.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Activity(Base):
    """
    Activity model for tracking user actions and events.
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: Owner user ID
        activity_type: Type of activity (query, report, dataset, login, etc.)
        title: Activity title/description
        description: Detailed description
        status: Activity status (success, failed, pending)
        metadata: Additional activity data (JSONB)
        created_at: Creation timestamp
    """
    
    __tablename__ = "activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=True)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    
    # Indexes
    __table_args__ = (
        Index("idx_activities_user_id", "user_id"),
        Index("idx_activities_created_at", "created_at"),
        Index("idx_activities_type", "activity_type"),
    )
    
    def __repr__(self) -> str:
        return f"<Activity(id={self.id}, type='{self.activity_type}')>"
    
    def to_dict(self) -> dict:
        """Convert activity to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.activity_type,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "metadata": self.metadata,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
            "icon": self._get_icon(),
            "color": self._get_color(),
        }
    
    def _get_icon(self) -> str:
        """Get icon based on activity type."""
        icons = {
            "query": "search",
            "report": "document",
            "dataset": "database",
            "login": "user",
            "upload": "upload",
            "export": "download",
        }
        return icons.get(self.activity_type, "activity")
    
    def _get_color(self) -> str:
        """Get color based on status."""
        colors = {
            "success": "#10B981",
            "completed": "#10B981",
            "ready": "#10B981",
            "failed": "#EF4444",
            "error": "#EF4444",
            "pending": "#F59E0B",
            "processing": "#3B82F6",
        }
        return colors.get(self.status, "#6B7280")
