"""
Datasets API routes for the Data Analyst Depth backend.

Provides endpoints for:
- Listing all uploaded datasets
- Uploading new datasets
- Getting dataset details
- Deleting datasets
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Dict, Any, List, Optional
import pandas as pd
import io
import json

from storage import storage
from auth import get_current_user

router = APIRouter(prefix="/datasets", tags=["datasets"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.get("")
async def list_datasets(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """List all uploaded datasets for the current user."""
    datasets = storage.list_datasets(user_id=current_user["id"])
    
    return {
        "datasets": [ds.to_dict() for ds in datasets],
        "total": len(datasets)
    }


@router.post("")
async def upload_dataset(
    file: UploadFile = File(...),
    sheet: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Upload and register a new dataset.
    Accepts CSV, XLSX, and JSON files. Max 50MB.
    """
    content = await file.read()
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large. Maximum size is 50MB.")
        
    filename = file.filename or "unnamed"
    base_name = filename.rsplit('.', 1)[0]
    
    # Check for name collisions
    existing_datasets = storage.list_datasets(user_id=current_user["id"])
    if any(ds.name == base_name for ds in existing_datasets):
        raise HTTPException(409, f"A dataset with the name '{base_name}' already exists.")
    
    try:
        # Parse based on file type
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith(('.xlsx', '.xls')):
            if sheet:
                df = pd.read_excel(io.BytesIO(content), sheet_name=sheet)
            else:
                df = pd.read_excel(io.BytesIO(content))
        elif filename.endswith('.json'):
            data = json.loads(content.decode('utf-8'))
            df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
        else:
            raise HTTPException(400, "Unsupported file type. Use CSV, XLSX, or JSON.")
        
        # Extract advanced schema
        columns = []
        for col in df.columns:
            # Calculate null percentage
            null_pct = round(df[col].isnull().mean() * 100, 2)
            
            # Extract sample values (up to 5 non-null distinct values)
            samples = df[col].dropna().astype(str).unique().tolist()[:5]
            
            columns.append({
                "name": str(col),
                "dtype": str(df[col].dtype),
                "null_percentage": null_pct,
                "sample_values": samples
            })
        
        # Get preview (first 5 rows)
        preview = df.head(5).to_dict(orient='records')
        
        # Add to storage
        dataset = storage.add_dataset(
            user_id=current_user["id"],
            name=base_name,
            filename=filename,
            size_bytes=len(content),
            row_count=len(df),
            column_count=len(df.columns),
            columns=columns,
            preview=preview
        )
        
        # Cache raw file bytes for download feature
        storage.store_file_content(dataset.id, content)
        
        return {
            "message": "Dataset uploaded successfully",
            "dataset": dataset.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Failed to parse file: {str(e)}")


@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed information about a specific dataset."""
    dataset = storage.get_dataset(dataset_id)
    
    if not dataset or dataset.user_id != current_user["id"]:
        raise HTTPException(404, "Dataset not found")
    
    return {"dataset": dataset.to_dict()}


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a dataset."""
    dataset = storage.get_dataset(dataset_id)
    
    if not dataset or dataset.user_id != current_user["id"]:
        raise HTTPException(404, "Dataset not found")
        
    storage.delete_dataset(dataset_id)
    
    return {"message": "Dataset deleted successfully"}


@router.patch("/{dataset_id}")
async def rename_dataset(
    dataset_id: str,
    name: str = Form(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Rename a dataset."""
    dataset = storage.get_dataset(dataset_id)
    
    if not dataset or dataset.user_id != current_user["id"]:
        raise HTTPException(404, "Dataset not found")
        
    if name == dataset.name:
        return {"dataset": dataset.to_dict()}
        
    # Check for collisions with other datasets owned by same user
    existing_datasets = storage.list_datasets(user_id=current_user["id"])
    if any(ds.name == name for ds in existing_datasets):
        raise HTTPException(409, f"A dataset with the name '{name}' already exists.")
        
    storage.rename_dataset(dataset_id, name)
    dataset.name = name
    
    return {"dataset": dataset.to_dict()}


@router.get("/{dataset_id}/preview")
async def get_dataset_preview(
    dataset_id: str,
    rows: int = 10,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get a preview of dataset contents (up to 100 rows)."""
    dataset = storage.get_dataset(dataset_id)
    
    if not dataset or dataset.user_id != current_user["id"]:
        raise HTTPException(404, "Dataset not found")
        
    limit = min(rows, 100)  # Max 100 rows
    
    return {
        "columns": dataset.columns,
        "preview": dataset.preview[:limit]
    }
