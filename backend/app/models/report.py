"""
Report Model

Defines the Report entity for generated analytical reports.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Report(Base):
    """
    Report model for generated analytical reports.
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: Owner user ID
        dataset_id: Associated dataset ID (optional)
        title: Report title
        query: Original query/prompt
        report_type: Type of report (summary, detailed, comparison)
        status: Processing status (pending, completed, failed)
        content: Generated report content
        summary: Report summary
        insights: List of insights (JSONB)
        metadata: Additional metadata (JSONB)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        completed_at: Completion timestamp
    """
    
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    query = Column(Text, nullable=False)
    report_type = Column(String(50), default="summary", nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    insights = Column(JSONB, nullable=True)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="reports")
    dataset = relationship("Dataset", back_populates="reports")
    
    # Indexes
    __table_args__ = (
        Index("idx_reports_user_id", "user_id"),
        Index("idx_reports_dataset_id", "dataset_id"),
        Index("idx_reports_status", "status"),
        Index("idx_reports_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Report(id={self.id}, title='{self.title}')>"
    
    def to_dict(self) -> dict:
        """Convert report to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "dataset_id": str(self.dataset_id) if self.dataset_id else None,
            "title": self.title,
            "query": self.query,
            "report_type": self.report_type,
            "status": self.status,
            "content": self.content,
            "summary": self.summary,
            "insights": self.insights or [],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
