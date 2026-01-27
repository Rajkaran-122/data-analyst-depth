"""
Common Schemas

Shared Pydantic models used across the application.
"""

from typing import Optional, List, Any, Dict, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    
    status: str = "success"
    data: Optional[T] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorDetail(BaseModel):
    """Error detail model."""
    
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    status: str = "error"
    error: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    
    items: List[T]
    total: int
    page: int = 1
    per_page: int = 20
    total_pages: int = 1
    has_next: bool = False
    has_prev: bool = False


class MessageResponse(BaseModel):
    """Simple message response."""
    
    message: str


class HealthCheck(BaseModel):
    """Health check for a single component."""
    
    status: str  # "healthy" or "unhealthy"
    message: Optional[str] = None
    latency_ms: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str  # "healthy" or "unhealthy"
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    components: Dict[str, HealthCheck] = {}


class StatsCard(BaseModel):
    """Dashboard statistics card model."""
    
    label: str
    value: Any
    change: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "stable"
    icon: Optional[str] = None
    color: Optional[str] = None


class ChartDataPoint(BaseModel):
    """Single data point for charts."""
    
    label: str
    value: float
    date: Optional[str] = None
    color: Optional[str] = None


class ChartData(BaseModel):
    """Chart data model."""
    
    chart_type: str  # "line", "bar", "pie", "area"
    labels: List[str] = []
    datasets: List[Dict[str, Any]] = []


class ActivityItem(BaseModel):
    """Activity feed item."""
    
    id: str
    type: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    timestamp: datetime
    icon: Optional[str] = None
    color: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
