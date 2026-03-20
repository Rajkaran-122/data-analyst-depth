"""
In-memory storage manager for the Data Analyst Depth backend.

Provides centralized storage for datasets, reports, and session analytics
without requiring external database dependencies.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
import uuid
import json


def _now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Dataset:
    """Represents an uploaded dataset."""
    id: str
    user_id: str
    name: str
    filename: str
    size_bytes: int
    row_count: int
    column_count: int
    columns: List[Dict[str, Any]]  # [{name, dtype, null_percentage, sample_values}]
    preview: List[Dict[str, Any]]  # First few rows
    uploaded_at: str
    status: str = "ready"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Dataset to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "filename": self.filename,
            "size_bytes": self.size_bytes,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "columns": self.columns,
            "preview": self.preview,
            "uploaded_at": self.uploaded_at,
            "status": self.status
        }



@dataclass
class Report:
    """Represents a generated analytical report."""
    id: str
    title: str
    dataset_id: Optional[str]
    query: str
    summary: str
    insights: List[str]
    created_at: str
    status: str = "completed"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Report to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "dataset_id": self.dataset_id,
            "query": self.query,
            "summary": self.summary,
            "insights": self.insights,
            "created_at": self.created_at,
            "status": self.status
        }


@dataclass
class QueryLog:
    """Represents a logged query for analytics."""
    id: str
    query: str
    dataset_id: Optional[str]
    response_time_ms: int
    status: str
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert QueryLog to dictionary."""
        return {
            "id": self.id,
            "query": self.query,
            "dataset_id": self.dataset_id,
            "response_time_ms": self.response_time_ms,
            "status": self.status,
            "timestamp": self.timestamp
        }


@dataclass
class Settings:
    """Represents user/application settings."""
    theme: str = "dark"
    language: str = "en"
    notifications_enabled: bool = True
    auto_refresh: bool = True
    refresh_interval: int = 30
    default_chart_type: str = "line"
    timezone: str = "UTC"
    api_keys: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Settings to dictionary."""
        return {
            "theme": self.theme,
            "language": self.language,
            "notifications_enabled": self.notifications_enabled,
            "auto_refresh": self.auto_refresh,
            "refresh_interval": self.refresh_interval,
            "default_chart_type": self.default_chart_type,
            "timezone": self.timezone,
            "api_keys": self.api_keys
        }


@dataclass
class Workspace:
    """Represents a data workspace for organizing datasets."""
    id: str
    name: str
    description: str
    color: str
    dataset_ids: List[str]
    created_at: str
    updated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Workspace to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "dataset_ids": self.dataset_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class StorageManager:
    """
    Central in-memory storage for all application data.
    
    Provides methods to manage datasets, reports, and query logs.
    Data persists only for the lifetime of the server process.
    """
    
    def __init__(self):
        self._datasets: Dict[str, Dataset] = {}
        self._reports: Dict[str, Report] = {}
        self._query_logs: List[QueryLog] = []
        self._workspaces: Dict[str, Workspace] = {}
        self._settings: Settings = Settings()
        self._max_query_logs = 1000
        
        # Analytics counters
        self._stats = {
            "total_queries": 0,
            "total_datasets": 0,
            "total_insights": 0,
            "active_sessions": 0,
        }
        
        # Initialize default workspaces
        self._init_default_workspaces()
    
    # -------------------------------------------------------------------------
    # Datasets
    # -------------------------------------------------------------------------
    
    def add_dataset(
        self,
        user_id: str,
        name: str,
        filename: str,
        size_bytes: int,
        row_count: int,
        column_count: int,
        columns: List[Dict[str, Any]],
        preview: List[Dict[str, Any]]
    ) -> Dataset:
        """Add a new dataset to storage."""
        uid_str: str = str(uuid.uuid4())
        dataset_id = uid_str[:8]
        dataset = Dataset(
            id=dataset_id,
            user_id=user_id,
            name=name,
            filename=filename,
            size_bytes=size_bytes,
            row_count=row_count,
            column_count=column_count,
            columns=columns,
            preview=preview,
            uploaded_at=_now_iso()
        )
        self._datasets[dataset_id] = dataset
        self._stats["total_datasets"] += 1
        return dataset
    
    def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        """Get a dataset by ID."""
        return self._datasets.get(dataset_id)
    
    def list_datasets(self, user_id: Optional[str] = None) -> List[Dataset]:
        """List all datasets. Optionally filter by user_id."""
        if user_id:
            return [ds for ds in self._datasets.values() if ds.user_id == user_id]
        return list(self._datasets.values())
    
    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset by ID."""
        if dataset_id in self._datasets:
            self._datasets.pop(dataset_id, None)
            return True
        return False
        
    def rename_dataset(self, dataset_id: str, new_name: str) -> bool:
        """Rename an existing dataset."""
        if dataset_id in self._datasets:
            self._datasets[dataset_id].name = new_name
            return True
        return False
    
    # -------------------------------------------------------------------------
    # Reports
    # -------------------------------------------------------------------------
    
    def add_report(
        self,
        title: str,
        query: str,
        summary: str,
        insights: List[str],
        dataset_id: Optional[str] = None
    ) -> Report:
        """Add a new report to storage."""
        uid_str: str = str(uuid.uuid4())
        report_id = uid_str[:8]
        report = Report(
            id=report_id,
            title=title,
            dataset_id=dataset_id,
            query=query,
            summary=summary,
            insights=insights,
            created_at=_now_iso()
        )
        self._reports[report_id] = report
        self._stats["total_insights"] += len(insights)
        return report
    
    def get_report(self, report_id: str) -> Optional[Report]:
        """Get a report by ID."""
        return self._reports.get(report_id)
    
    def list_reports(self) -> List[Report]:
        """List all reports."""
        return list(self._reports.values())
    
    # -------------------------------------------------------------------------
    # Query Logs
    # -------------------------------------------------------------------------
    
    def log_query(
        self,
        query: str,
        response_time_ms: int,
        status: str,
        dataset_id: Optional[str] = None
    ) -> QueryLog:
        """Log a query for analytics."""
        uid_str: str = str(uuid.uuid4())
        log_id = uid_str[:8]
        log = QueryLog(
            id=log_id,
            query=query,
            dataset_id=dataset_id,
            response_time_ms=response_time_ms,
            status=status,
            timestamp=_now_iso()
        )
        self._query_logs.append(log)
        self._stats["total_queries"] += 1
        
        # Trim old logs
        if len(self._query_logs) > self._max_query_logs:
            logs_count = len(self._query_logs)
            self._query_logs = self._query_logs[logs_count - self._max_query_logs:]
        
        return log
    
    def get_query_logs(self, limit: int = 100) -> List[QueryLog]:
        """Get recent query logs."""
        logs_count = len(self._query_logs)
        start_idx = max(0, logs_count - limit)
        return self._query_logs[start_idx:]
    
    # -------------------------------------------------------------------------
    # Dashboard Stats
    # -------------------------------------------------------------------------
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics for dashboard KPIs."""
        return {
            "total_queries": self._stats["total_queries"],
            "total_datasets": len(self._datasets),
            "total_insights": self._stats["total_insights"],
            "total_reports": len(self._reports),
            # Mocked growth percentages for UI
            "query_growth": 12.5,
            "dataset_growth": 8.2,
            "insight_growth": 24.5,
            "session_change": -2.1,
        }
    
    def get_query_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get query count trends for chart visualization."""
        # Generate sample trend data based on actual query count
        from datetime import timedelta
        import random
        
        base_count = max(10, self._stats["total_queries"])
        trends = []
        
        for i in range(days):
            date = datetime.now(timezone.utc) - timedelta(days=days - i - 1)
            # Simulate gradual growth with some variation
            count = int(base_count * (0.5 + (i / days) * 0.5) + random.randint(-5, 10))
            trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "queries": max(0, count),
            })
        
        return trends
    
    def get_source_distribution(self) -> List[Dict[str, Any]]:
        """Get data source distribution for pie chart."""
        datasets = self.list_datasets()
        
        if not datasets:
            # Return sample data if no datasets
            return [
                {"name": "CSV Files", "value": 45, "color": "#3B82F6"},
                {"name": "Excel Files", "value": 30, "color": "#8B5CF6"},
                {"name": "JSON Data", "value": 15, "color": "#06B6D4"},
                {"name": "API Sources", "value": 10, "color": "#10B981"},
            ]
        
        # Count by file extension
        extension_counts: Dict[str, int] = {}
        for ds in datasets:
            ext = ds.filename.split(".")[-1].upper() if "." in ds.filename else "OTHER"
            extension_counts[ext] = extension_counts.get(ext, 0) + 1
        
        colors = ["#3B82F6", "#8B5CF6", "#06B6D4", "#10B981", "#F59E0B", "#EF4444"]
        return [
            {"name": ext, "value": count, "color": colors[i % len(colors)]}
            for i, (ext, count) in enumerate(extension_counts.items())
        ]
    
    # -------------------------------------------------------------------------
    # Workspaces
    # -------------------------------------------------------------------------
    
    def _init_default_workspaces(self):
        """Initialize default workspaces on startup."""
        defaults = [
            {"id": "sales", "name": "Sales Analytics", "description": "Sales and revenue analysis", "color": "#3B82F6"},
            {"id": "marketing", "name": "Marketing", "description": "Marketing campaign analysis", "color": "#8B5CF6"},
            {"id": "finance", "name": "Financial", "description": "Financial data and reports", "color": "#10B981"},
        ]
        for ws in defaults:
            if ws["id"] not in self._workspaces:
                self._workspaces[ws["id"]] = Workspace(
                    id=ws["id"],
                    name=ws["name"],
                    description=ws["description"],
                    color=ws["color"],
                    dataset_ids=[],
                    created_at=_now_iso(),
                    updated_at=_now_iso()
                )
    
    def add_workspace(
        self,
        name: str,
        description: str = "",
        color: str = "#3B82F6"
    ) -> Workspace:
        """Add a new workspace."""
        uid_str: str = str(uuid.uuid4())
        workspace_id = uid_str[:8]
        workspace = Workspace(
            id=workspace_id,
            name=name,
            description=description,
            color=color,
            dataset_ids=[],
            created_at=_now_iso(),
            updated_at=_now_iso()
        )
        self._workspaces[workspace_id] = workspace
        return workspace
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get a workspace by ID."""
        return self._workspaces.get(workspace_id)
    
    def list_workspaces(self) -> List[Workspace]:
        """List all workspaces."""
        return list(self._workspaces.values())
    
    def update_workspace(
        self,
        workspace_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None
    ) -> Optional[Workspace]:
        """Update a workspace."""
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return None
        
        if name is not None:
            workspace.name = name
        if description is not None:
            workspace.description = description
        if color is not None:
            workspace.color = color
        workspace.updated_at = _now_iso()
        
        return workspace
    
    def delete_workspace(self, workspace_id: str) -> bool:
        """Delete a workspace."""
        if workspace_id in self._workspaces:
            self._workspaces.pop(workspace_id, None)
            return True
        return False
    
    def add_dataset_to_workspace(self, workspace_id: str, dataset_id: str) -> bool:
        """Link a dataset to a workspace."""
        workspace = self._workspaces.get(workspace_id)
        if workspace is None:
            return False
        
        # Ensure we check dataset_ids safely
        if dataset_id not in workspace.dataset_ids:
            workspace.dataset_ids.append(dataset_id)
            workspace.updated_at = _now_iso()
        return True
    
    def remove_dataset_from_workspace(self, workspace_id: str, dataset_id: str) -> bool:
        """Remove a dataset from a workspace."""
        workspace = self._workspaces.get(workspace_id)
        if not workspace or dataset_id not in workspace.dataset_ids:
            return False
        workspace.dataset_ids.remove(dataset_id)
        workspace.updated_at = _now_iso()
        return True
    
    # -------------------------------------------------------------------------
    # Settings
    # -------------------------------------------------------------------------
    
    def get_settings(self) -> Settings:
        """Get current settings."""
        return self._settings
    
    def update_settings(self, **kwargs) -> Settings:
        """Update settings with provided values."""
        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)
        return self._settings
    
    def add_api_key(self, key_name: str, key_value: str) -> bool:
        """Add or update an API key."""
        self._settings.api_keys[key_name] = key_value
        return True
    
    def remove_api_key(self, key_name: str) -> bool:
        """Remove an API key."""
        if key_name in self._settings.api_keys:
            self._settings.api_keys.pop(key_name, None)
            return True
        return False
    
    def get_api_keys(self) -> Dict[str, str]:
        """Get all API keys (masked)."""
        masked_keys = {}
        for name, value in self._settings.api_keys.items():
            val_str: str = str(value)
            masked_keys[name] = f"****{val_str[-4:]}" if len(val_str) > 4 else "****"
        return masked_keys


# Global storage instance
storage = StorageManager()

