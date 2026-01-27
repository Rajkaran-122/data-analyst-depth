"""
Workspace Model

Defines the Workspace entity for organizing datasets.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Workspace(Base):
    """
    Workspace model for organizing datasets.
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: Owner user ID
        name: Workspace name
        description: Optional description
        color: Color for UI display
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "workspaces"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(50), default="blue", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="workspaces")
    dataset_associations = relationship("WorkspaceDataset", back_populates="workspace", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_workspaces_user_id", "user_id"),
        Index("idx_workspaces_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Workspace(id={self.id}, name='{self.name}')>"
    
    @property
    def datasets(self):
        """Get list of associated datasets."""
        return [assoc.dataset for assoc in self.dataset_associations]
    
    @property
    def dataset_ids(self):
        """Get list of associated dataset IDs."""
        return [str(assoc.dataset_id) for assoc in self.dataset_associations]
    
    def to_dict(self, include_datasets: bool = False) -> dict:
        """Convert workspace to dictionary."""
        result = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "dataset_ids": self.dataset_ids,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_datasets:
            result["datasets"] = [d.to_dict() for d in self.datasets]
        
        return result


class WorkspaceDataset(Base):
    """
    Association table for Workspace-Dataset many-to-many relationship.
    """
    
    __tablename__ = "workspace_datasets"
    
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), primary_key=True)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="dataset_associations")
    dataset = relationship("Dataset", back_populates="workspace_associations")
    
    # Indexes
    __table_args__ = (
        Index("idx_workspace_datasets_workspace", "workspace_id"),
        Index("idx_workspace_datasets_dataset", "dataset_id"),
    )
    
    def __repr__(self) -> str:
        return f"<WorkspaceDataset(workspace={self.workspace_id}, dataset={self.dataset_id})>"
