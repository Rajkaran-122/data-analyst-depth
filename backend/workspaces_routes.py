"""
Workspaces API routes for the Data Analyst Depth backend.

Provides endpoints for:
- Creating and managing workspaces
- Linking datasets to workspaces
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from storage import storage

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


class CreateWorkspaceRequest(BaseModel):
    """Request model for creating a workspace."""
    name: str
    description: Optional[str] = ""
    color: Optional[str] = "#3B82F6"


class UpdateWorkspaceRequest(BaseModel):
    """Request model for updating a workspace."""
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


class LinkDatasetRequest(BaseModel):
    """Request model for linking a dataset to workspace."""
    dataset_id: str


@router.get("")
async def list_workspaces() -> Dict[str, Any]:
    """
    List all workspaces.
    
    Returns:
        List of workspaces with their datasets
    """
    workspaces = storage.list_workspaces()
    
    # Enhance with dataset counts
    result = []
    for ws in workspaces:
        ws_dict = ws.to_dict()
        ws_dict["dataset_count"] = len(ws.dataset_ids)
        # Get dataset details
        ws_dict["datasets"] = [
            storage.get_dataset(ds_id).to_dict() 
            for ds_id in ws.dataset_ids 
            if storage.get_dataset(ds_id)
        ]
        result.append(ws_dict)
    
    return {
        "workspaces": result,
        "total": len(result)
    }


@router.post("")
async def create_workspace(request: CreateWorkspaceRequest) -> Dict[str, Any]:
    """
    Create a new workspace.
    
    Args:
        request: Workspace creation parameters
    
    Returns:
        The created workspace
    """
    if not request.name:
        raise HTTPException(400, "Workspace name is required")
    
    workspace = storage.add_workspace(
        name=request.name,
        description=request.description or "",
        color=request.color or "#3B82F6"
    )
    
    return {
        "message": "Workspace created successfully",
        "workspace": workspace.to_dict()
    }


@router.get("/{workspace_id}")
async def get_workspace(workspace_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a workspace.
    
    Args:
        workspace_id: The workspace ID
    
    Returns:
        Workspace details including linked datasets
    """
    workspace = storage.get_workspace(workspace_id)
    
    if not workspace:
        raise HTTPException(404, "Workspace not found")
    
    ws_dict = workspace.to_dict()
    ws_dict["datasets"] = [
        storage.get_dataset(ds_id).to_dict() 
        for ds_id in workspace.dataset_ids 
        if storage.get_dataset(ds_id)
    ]
    
    return {"workspace": ws_dict}


@router.put("/{workspace_id}")
async def update_workspace(
    workspace_id: str,
    request: UpdateWorkspaceRequest
) -> Dict[str, Any]:
    """
    Update a workspace.
    
    Args:
        workspace_id: The workspace ID
        request: Update parameters
    
    Returns:
        Updated workspace
    """
    workspace = storage.update_workspace(
        workspace_id=workspace_id,
        name=request.name,
        description=request.description,
        color=request.color
    )
    
    if not workspace:
        raise HTTPException(404, "Workspace not found")
    
    return {
        "message": "Workspace updated successfully",
        "workspace": workspace.to_dict()
    }


@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id: str) -> Dict[str, Any]:
    """
    Delete a workspace.
    
    Args:
        workspace_id: The workspace ID to delete
    
    Returns:
        Confirmation message
    """
    success = storage.delete_workspace(workspace_id)
    
    if not success:
        raise HTTPException(404, "Workspace not found")
    
    return {"message": "Workspace deleted successfully"}


@router.post("/{workspace_id}/datasets")
async def link_dataset(
    workspace_id: str,
    request: LinkDatasetRequest
) -> Dict[str, Any]:
    """
    Link a dataset to a workspace.
    
    Args:
        workspace_id: The workspace ID
        request: Dataset link parameters
    
    Returns:
        Updated workspace
    """
    # Verify dataset exists
    dataset = storage.get_dataset(request.dataset_id)
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    
    success = storage.add_dataset_to_workspace(workspace_id, request.dataset_id)
    
    if not success:
        raise HTTPException(404, "Workspace not found")
    
    workspace = storage.get_workspace(workspace_id)
    
    return {
        "message": f"Dataset '{dataset.name}' linked to workspace",
        "workspace": workspace.to_dict()
    }


@router.delete("/{workspace_id}/datasets/{dataset_id}")
async def unlink_dataset(workspace_id: str, dataset_id: str) -> Dict[str, Any]:
    """
    Remove a dataset from a workspace.
    
    Args:
        workspace_id: The workspace ID
        dataset_id: The dataset ID to unlink
    
    Returns:
        Updated workspace
    """
    success = storage.remove_dataset_from_workspace(workspace_id, dataset_id)
    
    if not success:
        raise HTTPException(404, "Workspace or dataset link not found")
    
    workspace = storage.get_workspace(workspace_id)
    
    return {
        "message": "Dataset unlinked from workspace",
        "workspace": workspace.to_dict()
    }


@router.get("/{workspace_id}/stats")
async def get_workspace_stats(workspace_id: str) -> Dict[str, Any]:
    """
    Get statistics for a workspace.
    
    Args:
        workspace_id: The workspace ID
    
    Returns:
        Workspace statistics
    """
    workspace = storage.get_workspace(workspace_id)
    
    if not workspace:
        raise HTTPException(404, "Workspace not found")
    
    # Calculate stats
    total_rows = 0
    total_size = 0
    
    for ds_id in workspace.dataset_ids:
        dataset = storage.get_dataset(ds_id)
        if dataset:
            total_rows += dataset.row_count
            total_size += dataset.size_bytes
    
    return {
        "workspace_id": workspace_id,
        "stats": {
            "dataset_count": len(workspace.dataset_ids),
            "total_rows": total_rows,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    }
