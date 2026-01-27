"""
Workspace Schemas

Pydantic models for workspace management.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class WorkspaceBase(BaseModel):
    """Base workspace schema."""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    color: str = Field(default="blue", max_length=50)


class WorkspaceCreate(WorkspaceBase):
    """Workspace creation schema."""
    pass


class WorkspaceUpdate(BaseModel):
    """Workspace update schema (all fields optional)."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    color: Optional[str] = Field(None, max_length=50)


class WorkspaceResponse(BaseModel):
    """Workspace response schema."""
    
    id: str
    name: str
    description: Optional[str] = None
    color: str
    dataset_ids: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WorkspaceWithDatasets(WorkspaceResponse):
    """Workspace response with full dataset details."""
    
    datasets: List[dict] = []


class WorkspaceListResponse(BaseModel):
    """Workspace list response."""
    
    workspaces: List[WorkspaceResponse]
    total: int


class WorkspaceDatasetAdd(BaseModel):
    """Add dataset to workspace request."""
    
    dataset_id: str


class WorkspaceStats(BaseModel):
    """Workspace statistics."""
    
    dataset_count: int
    total_rows: int
    total_queries: int
    last_activity: Optional[datetime] = None
