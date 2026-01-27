"""
Datasets API Routes (Production)

Backward-compatible dataset management with database persistence.
"""

import os
import uuid
import aiofiles
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.dataset import Dataset
from app.models.activity import Activity
from app.models.workspace import WorkspaceDataset
from app.api.deps import CurrentUser, OptionalUser
from app.services.cache_service import cache, CacheKeys
from app.config import settings
from app.core.exceptions import NotFoundError, FileUploadError, FileTooLargeError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets", tags=["Datasets"])

# File type mappings
MIME_TO_TYPE = {
    "text/csv": "csv",
    "application/vnd.ms-excel": "xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/json": "json",
}


async def parse_file_metadata(file_path: str, file_type: str) -> Dict[str, Any]:
    """Parse file to extract metadata like row count, columns."""
    try:
        if file_type == "csv":
            import csv
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                row_count = sum(1 for _ in reader)
                return {
                    "columns": [{"name": col, "type": "string"} for col in headers],
                    "row_count": row_count,
                    "column_count": len(headers),
                }
        elif file_type == "json":
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    headers = list(data[0].keys()) if isinstance(data[0], dict) else []
                    return {
                        "columns": [{"name": col, "type": "string"} for col in headers],
                        "row_count": len(data),
                        "column_count": len(headers),
                    }
        # For Excel files, would need openpyxl
        return {"columns": [], "row_count": 0, "column_count": 0}
    except Exception as e:
        logger.error(f"Error parsing file metadata: {e}")
        return {"columns": [], "row_count": 0, "column_count": 0}


@router.get("")
async def list_datasets(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: object = Depends(OptionalUser),
):
    """
    List all datasets for the current user.
    
    Supports pagination and filtering by status.
    """
    # Build query
    query = db.query(Dataset)
    
    if current_user:
        query = query.filter(Dataset.user_id == current_user.id)
    else:
        # Return demo datasets for unauthenticated users
        return {
            "datasets": [
                {
                    "id": "demo-1",
                    "name": "Sales Data 2025",
                    "filename": "sales_2025.csv",
                    "file_type": "csv",
                    "status": "ready",
                    "row_count": 15000,
                    "column_count": 12,
                    "size_bytes": 1024000,
                    "created_at": datetime.utcnow().isoformat(),
                },
                {
                    "id": "demo-2",
                    "name": "Customer Analytics",
                    "filename": "customers.xlsx",
                    "file_type": "xlsx",
                    "status": "ready",
                    "row_count": 8500,
                    "column_count": 25,
                    "size_bytes": 2048000,
                    "created_at": datetime.utcnow().isoformat(),
                },
            ],
            "total": 2,
            "page": 1,
            "per_page": 20,
            "total_pages": 1,
        }
    
    if status_filter:
        query = query.filter(Dataset.status == status_filter)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    datasets = query.order_by(desc(Dataset.created_at)).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    
    return {
        "datasets": [ds.to_dict() for ds in datasets],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """
    Upload a new dataset file.
    
    Accepts CSV, Excel (xlsx, xls), and JSON files.
    Maximum file size: 50MB
    """
    # Validate file type
    file_ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if file_ext not in settings.allowed_extensions_list:
        raise FileUploadError(
            message=f"File type '{file_ext}' not allowed. Allowed: {settings.allowed_extensions_list}",
            code="VAL_002",
        )
    
    # Validate file size
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.max_upload_size:
        raise FileTooLargeError(
            message=f"File too large. Maximum size: {settings.max_upload_size // (1024*1024)}MB",
            max_size=settings.max_upload_size,
            actual_size=file_size,
        )
    
    # Create upload directory if needed
    upload_dir = settings.upload_dir
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}.{file_ext}")
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Parse file metadata
    file_type = MIME_TO_TYPE.get(file.content_type, file_ext)
    metadata = await parse_file_metadata(file_path, file_type)
    
    # Create dataset record
    dataset = Dataset(
        user_id=current_user.id,
        name=name or file.filename,
        filename=file.filename,
        file_path=file_path,
        file_type=file_type,
        status="ready",
        row_count=metadata.get("row_count"),
        column_count=metadata.get("column_count"),
        size_bytes=file_size,
        columns=metadata.get("columns"),
    )
    db.add(dataset)
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        activity_type="upload",
        title=f"Uploaded dataset: {dataset.name}",
        status="success",
        metadata={"dataset_id": str(dataset.id), "file_type": file_type},
    )
    db.add(activity)
    
    db.commit()
    db.refresh(dataset)
    
    logger.info(f"Dataset uploaded: {dataset.name} by user {current_user.email}")
    
    return {
        "message": "Dataset uploaded successfully",
        "dataset": dataset.to_dict(),
    }


@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: object = Depends(OptionalUser),
):
    """Get dataset details by ID."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    if not dataset:
        raise NotFoundError(
            message="Dataset not found",
            resource_type="dataset",
            resource_id=dataset_id,
        )
    
    # Check ownership if authenticated
    if current_user and str(dataset.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return dataset.to_dict()


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """Delete a dataset."""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    
    if not dataset:
        raise NotFoundError(
            message="Dataset not found",
            resource_type="dataset",
            resource_id=dataset_id,
        )
    
    # Delete file from disk
    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)
    
    # Remove from workspaces
    db.query(WorkspaceDataset).filter(
        WorkspaceDataset.dataset_id == dataset_id
    ).delete()
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        activity_type="delete",
        title=f"Deleted dataset: {dataset.name}",
        status="success",
    )
    db.add(activity)
    
    # Delete dataset
    db.delete(dataset)
    db.commit()
    
    # Invalidate cache
    cache.delete_pattern(f"dataset:*:{dataset_id}*")
    
    logger.info(f"Dataset deleted: {dataset_id} by user {current_user.email}")
    
    return {"message": "Dataset deleted successfully"}


@router.get("/{dataset_id}/preview")
async def preview_dataset(
    dataset_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: object = Depends(OptionalUser),
):
    """
    Get a preview of dataset contents.
    
    Returns first N rows of the dataset.
    """
    # Check cache
    cache_key = CacheKeys.dataset_preview(dataset_id, limit)
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    if not dataset:
        raise NotFoundError(
            message="Dataset not found",
            resource_type="dataset",
            resource_id=dataset_id,
        )
    
    # Check ownership if authenticated
    if current_user and str(dataset.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Read file and get preview
    try:
        if dataset.file_type == "csv":
            import csv
            with open(dataset.file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                rows = []
                for i, row in enumerate(reader):
                    if i >= limit:
                        break
                    rows.append(row)
                
                result = {
                    "columns": headers,
                    "rows": rows,
                    "total_rows": dataset.row_count or len(rows),
                    "showing": len(rows),
                }
        elif dataset.file_type == "json":
            import json
            with open(dataset.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    preview = data[:limit]
                    headers = list(preview[0].keys()) if preview else []
                    rows = [[row.get(h, "") for h in headers] for row in preview]
                    result = {
                        "columns": headers,
                        "rows": rows,
                        "total_rows": len(data),
                        "showing": len(preview),
                    }
                else:
                    result = {
                        "columns": list(data.keys()),
                        "rows": [[str(v) for v in data.values()]],
                        "total_rows": 1,
                        "showing": 1,
                    }
        else:
            result = {
                "columns": dataset.columns or [],
                "rows": [],
                "total_rows": dataset.row_count or 0,
                "showing": 0,
                "message": "Preview not available for this file type",
            }
        
        # Cache for 10 minutes
        cache.set(cache_key, result, 600)
        
        return result
        
    except Exception as e:
        logger.error(f"Error reading dataset {dataset_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error reading dataset file"
        )
