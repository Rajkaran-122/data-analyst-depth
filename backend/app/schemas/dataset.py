"""
Dataset Schemas

Pydantic models for dataset management.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DatasetBase(BaseModel):
    """Base dataset schema."""
    
    name: str = Field(..., min_length=1, max_length=255)


class DatasetCreate(DatasetBase):
    """Dataset creation schema (used with file upload)."""
    pass


class DatasetResponse(BaseModel):
    """Dataset response schema."""
    
    id: str
    name: str
    filename: str
    file_type: str
    status: str
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    size_bytes: Optional[int] = None
    columns: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DatasetListItem(BaseModel):
    """Dataset list item (minimal info)."""
    
    id: str
    name: str
    filename: str
    file_type: str
    status: str
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None


class DatasetListResponse(BaseModel):
    """Paginated dataset list response."""
    
    datasets: List[DatasetListItem]
    total: int
    page: int = 1
    per_page: int = 20
    total_pages: int = 1


class DatasetColumn(BaseModel):
    """Dataset column metadata."""
    
    name: str
    type: str
    nullable: bool = True
    unique_count: Optional[int] = None
    sample_values: Optional[List[Any]] = None


class DatasetPreview(BaseModel):
    """Dataset preview response."""
    
    columns: List[str]
    rows: List[List[Any]]
    total_rows: int
    column_types: Optional[Dict[str, str]] = None


class DatasetStats(BaseModel):
    """Dataset statistics."""
    
    row_count: int
    column_count: int
    size_bytes: int
    file_type: str
    null_counts: Optional[Dict[str, int]] = None
    numeric_columns: Optional[List[str]] = None
    categorical_columns: Optional[List[str]] = None


class DatasetUploadResponse(BaseModel):
    """Response after successful dataset upload."""
    
    message: str = "Dataset uploaded successfully"
    dataset: DatasetResponse
