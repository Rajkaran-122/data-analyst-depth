import os
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field

from database import SessionLocal
from models import DatasetMeta, ReportMeta, QueryLogDB, WorkspaceDB

# Ensure data lake exists
DATA_LAKE_DIR = "./data_lake"
os.makedirs(DATA_LAKE_DIR, exist_ok=True)

def _now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()

@dataclass
class Dataset:
    id: str
    user_id: str
    name: str
    filename: str
    size_bytes: int
    row_count: int
    column_count: int
    columns: List[Dict[str, Any]]
    preview: List[Dict[str, Any]]
    uploaded_at: str
    status: str = "ready"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "user_id": self.user_id, "name": self.name,
            "filename": self.filename, "size_bytes": self.size_bytes,
            "row_count": self.row_count, "column_count": self.column_count,
            "columns": self.columns, "preview": self.preview,
            "uploaded_at": self.uploaded_at, "status": self.status
        }

@dataclass
class Report:
    id: str
    title: str
    dataset_id: Optional[str]
    query: str
    summary: str
    insights: List[str]
    created_at: str
    status: str = "completed"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "title": self.title, "dataset_id": self.dataset_id,
            "query": self.query, "summary": self.summary, "insights": self.insights,
            "created_at": self.created_at, "status": self.status
        }

@dataclass
class QueryLog:
    id: str
    query: str
    dataset_id: Optional[str]
    response_time_ms: int
    status: str
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
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
    theme: str = "dark"
    language: str = "en"
    notifications_enabled: bool = True
    auto_refresh: bool = True
    refresh_interval: int = 30
    default_chart_type: str = "line"
    timezone: str = "UTC"
    api_keys: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
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
    id: str
    name: str
    description: str
    color: str
    dataset_ids: List[str]
    created_at: str
    updated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
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
    """Persistent storage acting as a seamless replacement for the old in-memory db."""
    
    def __init__(self):
        self._settings = Settings()
        self._download_logs = []
        self._init_default_workspaces()
        
    def _to_dataset(self, meta: DatasetMeta) -> Dataset:
        return Dataset(
            id=meta.id, user_id=meta.user_id, name=meta.name, filename=meta.filename,
            size_bytes=meta.size_bytes, row_count=meta.row_count, column_count=meta.column_count,
            columns=meta.columns, preview=meta.preview, uploaded_at=meta.uploaded_at, status=meta.status
        )

    def _to_report(self, meta: ReportMeta) -> Report:
        return Report(
            id=meta.id, title=meta.title, dataset_id=meta.dataset_id, query=meta.query,
            summary=meta.summary, insights=meta.insights, created_at=meta.created_at, status=meta.status
        )

    def _to_query_log(self, db_log: QueryLogDB) -> QueryLog:
        return QueryLog(
            id=db_log.id, query=db_log.query, dataset_id=db_log.dataset_id, 
            response_time_ms=db_log.response_time_ms, status=db_log.status, timestamp=db_log.timestamp
        )

    def _to_workspace(self, db_ws: WorkspaceDB) -> Workspace:
        return Workspace(
            id=db_ws.id, name=db_ws.name, description=db_ws.description, color=db_ws.color,
            dataset_ids=db_ws.dataset_ids, created_at=db_ws.created_at, updated_at=db_ws.updated_at
        )

    # ---------------- Datasets ----------------
    def add_dataset(self, user_id: str, name: str, filename: str, size_bytes: int, row_count: int, column_count: int, columns: List[Dict[str, Any]], preview: List[Dict[str, Any]]) -> Dataset:
        uid_str: str = str(uuid.uuid4())[:8]
        with SessionLocal() as db:
            obj = DatasetMeta(id=uid_str, user_id=user_id, name=name, filename=filename, size_bytes=size_bytes, row_count=row_count, column_count=column_count, columns=columns, preview=preview, uploaded_at=_now_iso(), status="ready")
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return self._to_dataset(obj)
            
    def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        with SessionLocal() as db:
            obj = db.query(DatasetMeta).filter(DatasetMeta.id == dataset_id).first()
            return self._to_dataset(obj) if obj else None

    def list_datasets(self, user_id: Optional[str] = None) -> List[Dataset]:
        with SessionLocal() as db:
            query = db.query(DatasetMeta)
            if user_id: query = query.filter(DatasetMeta.user_id == user_id)
            return [self._to_dataset(obj) for obj in query.all()]
            
    def delete_dataset(self, dataset_id: str) -> bool:
        with SessionLocal() as db:
            obj = db.query(DatasetMeta).filter(DatasetMeta.id == dataset_id).first()
            if obj:
                db.delete(obj)
                db.commit()
                # Delete from physical storage
                filepath = os.path.join(DATA_LAKE_DIR, dataset_id)
                if os.path.exists(filepath):
                    os.remove(filepath)
                return True
        return False
        
    def rename_dataset(self, dataset_id: str, new_name: str) -> bool:
        with SessionLocal() as db:
            obj = db.query(DatasetMeta).filter(DatasetMeta.id == dataset_id).first()
            if obj:
                obj.name = new_name
                db.commit()
                return True
        return False

    # ---------------- Reports ----------------
    def add_report(self, title: str, query: str, summary: str, insights: List[str], dataset_id: Optional[str] = None) -> Report:
        uid_str: str = str(uuid.uuid4())[:8]
        with SessionLocal() as db:
            obj = ReportMeta(id=uid_str, title=title, dataset_id=dataset_id, query=query, summary=summary, insights=insights, created_at=_now_iso())
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return self._to_report(obj)
            
    def get_report(self, report_id: str) -> Optional[Report]:
        with SessionLocal() as db:
            obj = db.query(ReportMeta).filter(ReportMeta.id == report_id).first()
            return self._to_report(obj) if obj else None

    def list_reports(self) -> List[Report]:
        with SessionLocal() as db:
            return [self._to_report(obj) for obj in db.query(ReportMeta).all()]

    # ---------------- Query Logs ----------------
    def log_query(self, query: str, response_time_ms: int, status: str, dataset_id: Optional[str] = None) -> QueryLog:
        uid_str: str = str(uuid.uuid4())[:8]
        with SessionLocal() as db:
            obj = QueryLogDB(id=uid_str, query=query, dataset_id=dataset_id, response_time_ms=response_time_ms, status=status, timestamp=_now_iso())
            db.add(obj)
            
            # Simple trim 
            if db.query(QueryLogDB).count() > 1000:
                oldest = db.query(QueryLogDB).order_by(QueryLogDB.timestamp.asc()).first()
                if oldest: db.delete(oldest)
            
            db.commit()
            db.refresh(obj)
            return self._to_query_log(obj)
            
    def get_query_logs(self, limit: int = 100) -> List[QueryLog]:
        with SessionLocal() as db:
            logs = db.query(QueryLogDB).order_by(QueryLogDB.timestamp.desc()).limit(limit).all()
            return [self._to_query_log(obj) for obj in logs][::-1]

    # ---------------- Dashboards ----------------
    def get_dashboard_stats(self) -> Dict[str, Any]:
        with SessionLocal() as db:
            return {
                "total_queries": db.query(QueryLogDB).count(),
                "total_datasets": db.query(DatasetMeta).count(),
                "total_insights": db.query(ReportMeta).count() * 3, # Mock projection
                "total_reports": db.query(ReportMeta).count(),
                "query_growth": 12.5, "dataset_growth": 8.2, "insight_growth": 24.5, "session_change": -2.1,
            }
            
    def get_query_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        from datetime import timedelta
        import random
        base_count = max(10, self.get_dashboard_stats()["total_queries"])
        trends = []
        for i in range(days):
            date = datetime.now(timezone.utc) - timedelta(days=days - i - 1)
            trends.append({"date": date.strftime("%Y-%m-%d"), "queries": max(0, int(base_count * (0.5 + (i / days) * 0.5) + random.randint(-5, 10)))})
        return trends
        
    def get_source_distribution(self) -> List[Dict[str, Any]]:
        datasets = self.list_datasets()
        if not datasets:
            return [
                {"name": "CSV Files", "value": 45, "color": "#3B82F6"},
                {"name": "Excel Files", "value": 30, "color": "#8B5CF6"},
                {"name": "JSON Data", "value": 15, "color": "#06B6D4"}
            ]
        counts = {}
        for ds in datasets:
            ext = ds.filename.split(".")[-1].upper() if "." in ds.filename else "OTHER"
            counts[ext] = counts.get(ext, 0) + 1
        colors = ["#3B82F6", "#8B5CF6", "#06B6D4", "#10B981"]
        return [{"name": ext, "value": count, "color": colors[i % len(colors)]} for i, (ext, count) in enumerate(counts.items())]

    # ---------------- Workspaces ----------------
    def _init_default_workspaces(self):
        with SessionLocal() as db:
            if db.query(WorkspaceDB).count() == 0:
                defaults = [
                    WorkspaceDB(id="sales", name="Sales Analytics", description="Sales analysis", color="#3B82F6", dataset_ids=[], created_at=_now_iso(), updated_at=_now_iso()),
                    WorkspaceDB(id="marketing", name="Marketing", description="Campaign analytics", color="#8B5CF6", dataset_ids=[], created_at=_now_iso(), updated_at=_now_iso())
                ]
                db.add_all(defaults)
                db.commit()

    def add_workspace(self, name: str, description: str = "", color: str = "#3B82F6") -> Workspace:
        uid_str: str = str(uuid.uuid4())[:8]
        with SessionLocal() as db:
            obj = WorkspaceDB(id=uid_str, name=name, description=description, color=color, dataset_ids=[], created_at=_now_iso(), updated_at=_now_iso())
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return self._to_workspace(obj)
            
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        with SessionLocal() as db:
            obj = db.query(WorkspaceDB).filter(WorkspaceDB.id == workspace_id).first()
            return self._to_workspace(obj) if obj else None

    def list_workspaces(self) -> List[Workspace]:
        with SessionLocal() as db:
            return [self._to_workspace(w) for w in db.query(WorkspaceDB).all()]

    def update_workspace(self, workspace_id: str, name: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None) -> Optional[Workspace]:
        with SessionLocal() as db:
            obj = db.query(WorkspaceDB).filter(WorkspaceDB.id == workspace_id).first()
            if obj:
                if name: obj.name = name
                if description: obj.description = description
                if color: obj.color = color
                obj.updated_at = _now_iso()
                db.commit()
                db.refresh(obj)
                return self._to_workspace(obj)
        return None

    def delete_workspace(self, workspace_id: str) -> bool:
        with SessionLocal() as db:
            obj = db.query(WorkspaceDB).filter(WorkspaceDB.id == workspace_id).first()
            if obj:
                db.delete(obj)
                db.commit()
                return True
        return False
        
    def add_dataset_to_workspace(self, workspace_id: str, dataset_id: str) -> bool:
        with SessionLocal() as db:
            obj = db.query(WorkspaceDB).filter(WorkspaceDB.id == workspace_id).first()
            if obj and dataset_id not in obj.dataset_ids:
                temp = list(obj.dataset_ids)
                temp.append(dataset_id)
                obj.dataset_ids = temp
                db.commit()
                return True
        return False

    def remove_dataset_from_workspace(self, workspace_id: str, dataset_id: str) -> bool:
        with SessionLocal() as db:
            obj = db.query(WorkspaceDB).filter(WorkspaceDB.id == workspace_id).first()
            if obj and dataset_id in obj.dataset_ids:
                temp = list(obj.dataset_ids)
                temp.remove(dataset_id)
                obj.dataset_ids = temp
                db.commit()
                return True
        return False

    # ---------------- Physical File Storage ----------------
    def store_file_content(self, dataset_id: str, content: bytes) -> None:
        """Cache raw bytes to disk."""
        filepath = os.path.join(DATA_LAKE_DIR, dataset_id)
        with open(filepath, 'wb') as f:
            f.write(content)
            
    def get_file_content(self, dataset_id: str) -> Optional[bytes]:
        """Retrieve cached raw bytes from disk."""
        filepath = os.path.join(DATA_LAKE_DIR, dataset_id)
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                return f.read()
        return None

    # ---------------- Miscellaneous ----------------
    def get_settings(self) -> Settings: return self._settings
    def update_settings(self, **kwargs) -> Settings:
        for k, v in kwargs.items():
            if hasattr(self._settings, k): setattr(self._settings, k, v)
        return self._settings
    def add_api_key(self, n: str, v: str) -> bool: self._settings.api_keys[n] = v; return True
    def remove_api_key(self, n: str) -> bool: return self._settings.api_keys.pop(n, None) is not None
    def get_api_keys(self) -> Dict[str, str]:
        return {n: f"****{str(v)[-4:]}" if len(str(v)) > 4 else "****" for n,v in self._settings.api_keys.items()}
        
    def record_download(self, dataset_id: str, download_type: str, fmt: str, row_count: int, size_bytes: int) -> None:
        self._download_logs.append({
            "dataset_id": dataset_id, "download_type": download_type, "format": fmt,
            "row_count": row_count, "size_bytes": size_bytes, "timestamp": _now_iso()
        })
        if len(self._download_logs) > 500: self._download_logs = self._download_logs[-500:]

    def get_download_stats(self) -> Dict[str, Any]:
        return {"total_downloads": len(self._download_logs), "recent_downloads": self._download_logs[-20:][::-1]}

# Global storage instance
storage = StorageManager()
