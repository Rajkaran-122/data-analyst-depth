"""
Report Schemas

Pydantic models for report management.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ReportType(str, Enum):
    """Report type enumeration."""
    
    SUMMARY = "summary"
    DETAILED = "detailed"
    COMPARISON = "comparison"


class ReportStatus(str, Enum):
    """Report status enumeration."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportFormat(str, Enum):
    """Export format enumeration."""
    
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"


class ReportCreate(BaseModel):
    """Report generation request schema."""
    
    title: str = Field(..., min_length=1, max_length=500)
    query: str = Field(..., min_length=1)
    dataset_id: Optional[str] = None
    report_type: ReportType = ReportType.SUMMARY


class ReportResponse(BaseModel):
    """Report response schema."""
    
    id: str
    title: str
    query: str
    report_type: str
    status: str
    content: Optional[str] = None
    summary: Optional[str] = None
    insights: List[Dict[str, Any]] = []
    dataset_id: Optional[str] = None
    dataset_name: Optional[str] = None
    insight_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ReportListItem(BaseModel):
    """Report list item (minimal info)."""
    
    id: str
    title: str
    report_type: str
    status: str
    insight_count: int = 0
    dataset_name: Optional[str] = None
    created_at: Optional[datetime] = None


class ReportListResponse(BaseModel):
    """Paginated report list response."""
    
    reports: List[ReportListItem]
    total: int
    page: int = 1
    per_page: int = 20
    summary: Dict[str, int] = {}  # completed, pending, failed counts


class ReportExport(BaseModel):
    """Report export response."""
    
    format: str
    content: str
    filename: str
    mime_type: str


class ReportTemplate(BaseModel):
    """Report template schema."""
    
    id: str
    name: str
    description: str
    type: str
    sample_query: Optional[str] = None


class ReportTemplateList(BaseModel):
    """Report template list response."""
    
    templates: List[ReportTemplate]


class ReportGenerateResponse(BaseModel):
    """Response after report generation request."""
    
    message: str = "Report generation started"
    report: ReportResponse
