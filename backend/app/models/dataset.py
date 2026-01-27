"""
Dataset Model

Defines the Dataset entity for uploaded data files.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Dataset(Base):
    """
    Dataset model for uploaded data files.
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: Owner user ID
        name: Dataset display name
        filename: Original filename
        file_path: Storage path
        file_type: File extension (csv, xlsx, json)
        status: Processing status (ready, processing, failed)
        row_count: Number of rows in dataset
        column_count: Number of columns
        size_bytes: File size in bytes
        columns: Column metadata (JSONB)
        metadata: Additional metadata (JSONB)
        created_at: Upload timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "datasets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    status = Column(String(50), default="ready", nullable=False)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    columns = Column(JSONB, nullable=True)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="datasets")
    reports = relationship("Report", back_populates="dataset")
    queries = relationship("Query", back_populates="dataset")
    workspace_associations = relationship("WorkspaceDataset", back_populates="dataset", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_datasets_user_id", "user_id"),
        Index("idx_datasets_created_at", "created_at"),
        Index("idx_datasets_status", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<Dataset(id={self.id}, name='{self.name}')>"
    
    def to_dict(self) -> dict:
        """Convert dataset to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "filename": self.filename,
            "file_type": self.file_type,
            "status": self.status,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "size_bytes": self.size_bytes,
            "columns": self.columns,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
