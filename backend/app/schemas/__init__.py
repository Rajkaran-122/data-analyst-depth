"""
Pydantic Schemas Package

Contains all Pydantic models for request/response validation.
"""

from app.schemas.common import (
    ResponseModel,
    PaginatedResponse,
    HealthResponse,
    MessageResponse,
)
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    TokenRefreshRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.schemas.dataset import (
    DatasetCreate,
    DatasetResponse,
    DatasetListResponse,
    DatasetPreview,
)
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceDatasetAdd,
)
from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportExport,
    ReportTemplate,
)
from app.schemas.settings_schema import (
    SettingsUpdate,
    SettingsResponse,
    ApiKeyCreate,
    ApiKeyResponse,
)

__all__ = [
    # Common
    "ResponseModel",
    "PaginatedResponse",
    "HealthResponse",
    "MessageResponse",
    # User
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "TokenRefreshRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    # Dataset
    "DatasetCreate",
    "DatasetResponse",
    "DatasetListResponse",
    "DatasetPreview",
    # Workspace
    "WorkspaceCreate",
    "WorkspaceUpdate",
    "WorkspaceResponse",
    "WorkspaceDatasetAdd",
    # Report
    "ReportCreate",
    "ReportResponse",
    "ReportExport",
    "ReportTemplate",
    # Settings
    "SettingsUpdate",
    "SettingsResponse",
    "ApiKeyCreate",
    "ApiKeyResponse",
]
