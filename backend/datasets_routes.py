"""
Datasets API routes for the Data Analyst Depth backend.

Provides endpoints for:
- Listing all uploaded datasets
- Uploading new datasets
- Getting dataset details
- Deleting datasets
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any, List
import pandas as pd
import io
import json

from storage import storage

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("")
async def list_datasets() -> Dict[str, Any]:
    """
    List all uploaded datasets with metadata.
    
    Returns:
        Dictionary containing list of datasets with metadata
    """
    datasets = storage.list_datasets()
    
    return {
        "datasets": [ds.to_dict() for ds in datasets],
        "total": len(datasets)
    }


@router.post("")
async def upload_dataset(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and register a new dataset.
    
    Accepts CSV, XLSX, and JSON files.
    
    Args:
        file: The uploaded file
    
    Returns:
        The created dataset metadata
    """
    filename = file.filename or "unnamed"
    content = await file.read()
    
    try:
        # Parse based on file type
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        elif filename.endswith('.json'):
            data = json.loads(content.decode('utf-8'))
            df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
        else:
            raise HTTPException(400, "Unsupported file type. Use CSV, XLSX, or JSON.")
        
        # Extract schema
        columns = [
            {"name": col, "dtype": str(df[col].dtype)}
            for col in df.columns
        ]
        
        # Get preview (first 5 rows)
        preview = df.head(5).to_dict(orient='records')
        
        # Add to storage
        dataset = storage.add_dataset(
            name=filename.rsplit('.', 1)[0],
            filename=filename,
            size_bytes=len(content),
            row_count=len(df),
            column_count=len(df.columns),
            columns=columns,
            preview=preview
        )
        
        return {
            "message": "Dataset uploaded successfully",
            "dataset": dataset.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Failed to parse file: {str(e)}")


@router.get("/{dataset_id}")
async def get_dataset(dataset_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific dataset.
    
    Args:
        dataset_id: The dataset ID
    
    Returns:
        Dataset details including schema and preview
    """
    dataset = storage.get_dataset(dataset_id)
    
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    
    return {"dataset": dataset.to_dict()}


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str) -> Dict[str, Any]:
    """
    Delete a dataset.
    
    Args:
        dataset_id: The dataset ID to delete
    
    Returns:
        Confirmation message
    """
    success = storage.delete_dataset(dataset_id)
    
    if not success:
        raise HTTPException(404, "Dataset not found")
    
    return {"message": "Dataset deleted successfully"}


@router.get("/{dataset_id}/preview")
async def get_dataset_preview(dataset_id: str, rows: int = 10) -> Dict[str, Any]:
    """
    Get a preview of dataset contents.
    
    Args:
        dataset_id: The dataset ID
        rows: Number of rows to return
    
    Returns:
        Preview rows from the dataset
    """
    dataset = storage.get_dataset(dataset_id)
    
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    
    return {
        "columns": dataset.columns,
        "preview": dataset.preview[:rows]
    }
