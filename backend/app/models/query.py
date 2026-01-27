"""
Query Model

Defines the Query entity for tracking user queries/analyses.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Query(Base):
    """
    Query model for tracking user queries and AI analyses.
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: Owner user ID
        dataset_id: Associated dataset ID (optional)
        query_text: User's query text
        response: AI response text
        context: Query context (JSONB)
        execution_time_ms: Query execution time in milliseconds
        status: Query status (completed, failed)
        source: Query source (explorer, chat, api)
        created_at: Creation timestamp
    """
    
    __tablename__ = "queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True, index=True)
    query_text = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    context = Column(JSONB, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    status = Column(String(50), default="completed", nullable=False)
    source = Column(String(50), default="api", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="queries")
    dataset = relationship("Dataset", back_populates="queries")
    
    # Indexes
    __table_args__ = (
        Index("idx_queries_user_id", "user_id"),
        Index("idx_queries_dataset_id", "dataset_id"),
        Index("idx_queries_created_at", "created_at"),
        Index("idx_queries_status", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<Query(id={self.id})>"
    
    def to_dict(self) -> dict:
        """Convert query to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "dataset_id": str(self.dataset_id) if self.dataset_id else None,
            "query_text": self.query_text,
            "response": self.response,
            "context": self.context,
            "execution_time_ms": self.execution_time_ms,
            "status": self.status,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
