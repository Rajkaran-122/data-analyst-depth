"""
Workspaces API Routes (Production)

Backward-compatible workspace management with database persistence.
"""

from datetime import datetime
from typing import List, Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.workspace import Workspace, WorkspaceDataset
from app.models.dataset import Dataset
from app.models.activity import Activity
from app.api.deps import CurrentUser, OptionalUser
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("")
async def list_workspaces(
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    List all workspaces for the current user.
    """
    if current_user:
        workspaces = db.query(Workspace).filter(
            Workspace.user_id == current_user.id
        ).order_by(desc(Workspace.created_at)).all()
        
        return {
            "workspaces": [ws.to_dict() for ws in workspaces],
            "total": len(workspaces),
        }
    
    # Demo workspaces
    return {
        "workspaces": [
            {
                "id": "demo-1",
                "name": "Sales Analytics",
                "description": "Sales performance and analysis",
                "color": "blue",
                "dataset_ids": ["demo-ds-1", "demo-ds-2"],
                "created_at": datetime.utcnow().isoformat(),
            },
            {
                "id": "demo-2",
                "name": "Marketing",
                "description": "Marketing campaigns and metrics",
                "color": "purple",
                "dataset_ids": ["demo-ds-3"],
                "created_at": datetime.utcnow().isoformat(),
            },
            {
                "id": "demo-3",
                "name": "Financial",
                "description": "Financial reports and analysis",
                "color": "green",
                "dataset_ids": [],
                "created_at": datetime.utcnow().isoformat(),
            },
        ],
        "total": 3,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workspace(
    name: str,
    description: Optional[str] = None,
    color: str = "blue",
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """
    Create a new workspace.
    """
    workspace = Workspace(
        user_id=current_user.id,
        name=name,
        description=description,
        color=color,
    )
    db.add(workspace)
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        activity_type="workspace",
        title=f"Created workspace: {name}",
        status="success",
    )
    db.add(activity)
    
    db.commit()
    db.refresh(workspace)
    
    return {
        "message": "Workspace created successfully",
        "workspace": workspace.to_dict(),
    }


@router.get("/{workspace_id}")
async def get_workspace(
    workspace_id: str,
    include_datasets: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Get workspace details by ID.
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    if not workspace:
        raise NotFoundError(
            message="Workspace not found",
            resource_type="workspace",
            resource_id=workspace_id,
        )
    
    # Check ownership if authenticated
    if current_user and str(workspace.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return workspace.to_dict(include_datasets=include_datasets)


@router.put("/{workspace_id}")
async def update_workspace(
    workspace_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    color: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """
    Update a workspace.
    """
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise NotFoundError(
            message="Workspace not found",
            resource_type="workspace",
            resource_id=workspace_id,
        )
    
    if name is not None:
        workspace.name = name
    if description is not None:
        workspace.description = description
    if color is not None:
        workspace.color = color
    
    workspace.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(workspace)
    
    return {
        "message": "Workspace updated successfully",
        "workspace": workspace.to_dict(),
    }


@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """
    Delete a workspace.
    """
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise NotFoundError(
            message="Workspace not found",
            resource_type="workspace",
            resource_id=workspace_id,
        )
    
    workspace_name = workspace.name
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        activity_type="delete",
        title=f"Deleted workspace: {workspace_name}",
        status="success",
    )
    db.add(activity)
    
    db.delete(workspace)
    db.commit()
    
    return {"message": "Workspace deleted successfully"}


@router.post("/{workspace_id}/datasets")
async def add_dataset_to_workspace(
    workspace_id: str,
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """
    Add a dataset to a workspace.
    """
    # Verify workspace ownership
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise NotFoundError(
            message="Workspace not found",
            resource_type="workspace",
            resource_id=workspace_id,
        )
    
    # Verify dataset ownership
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
    
    # Check if already linked
    existing = db.query(WorkspaceDataset).filter(
        WorkspaceDataset.workspace_id == workspace_id,
        WorkspaceDataset.dataset_id == dataset_id
    ).first()
    
    if existing:
        return {"message": "Dataset already in workspace"}
    
    # Add link
    link = WorkspaceDataset(
        workspace_id=workspace_id,
        dataset_id=dataset_id,
    )
    db.add(link)
    db.commit()
    
    return {
        "message": f"Dataset '{dataset.name}' added to workspace '{workspace.name}'",
    }


@router.delete("/{workspace_id}/datasets/{dataset_id}")
async def remove_dataset_from_workspace(
    workspace_id: str,
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """
    Remove a dataset from a workspace.
    """
    # Verify workspace ownership
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise NotFoundError(
            message="Workspace not found",
            resource_type="workspace",
            resource_id=workspace_id,
        )
    
    # Remove link
    result = db.query(WorkspaceDataset).filter(
        WorkspaceDataset.workspace_id == workspace_id,
        WorkspaceDataset.dataset_id == dataset_id
    ).delete()
    
    db.commit()
    
    if result == 0:
        return {"message": "Dataset not in workspace"}
    
    return {"message": "Dataset removed from workspace"}


@router.get("/{workspace_id}/stats")
async def get_workspace_stats(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Get statistics for a workspace.
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    if not workspace:
        raise NotFoundError(
            message="Workspace not found",
            resource_type="workspace",
            resource_id=workspace_id,
        )
    
    # Count datasets
    dataset_count = db.query(func.count(WorkspaceDataset.dataset_id)).filter(
        WorkspaceDataset.workspace_id == workspace_id
    ).scalar() or 0
    
    # Get total rows across datasets
    dataset_ids = [assoc.dataset_id for assoc in workspace.dataset_associations]
    total_rows = 0
    if dataset_ids:
        total_rows = db.query(func.sum(Dataset.row_count)).filter(
            Dataset.id.in_(dataset_ids)
        ).scalar() or 0
    
    return {
        "workspace_id": str(workspace.id),
        "workspace_name": workspace.name,
        "dataset_count": dataset_count,
        "total_rows": total_rows,
        "total_queries": 0,  # Would need to track per-workspace queries
        "last_activity": workspace.updated_at.isoformat() if workspace.updated_at else None,
    }
