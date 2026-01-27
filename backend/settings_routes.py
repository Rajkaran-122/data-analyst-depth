"""
Settings API routes for the Data Analyst Depth backend.

Provides endpoints for:
- Getting and updating application settings
- Managing API keys
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from storage import storage

router = APIRouter(prefix="/settings", tags=["settings"])


class UpdateSettingsRequest(BaseModel):
    """Request model for updating settings."""
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    auto_refresh: Optional[bool] = None
    refresh_interval: Optional[int] = None
    default_chart_type: Optional[str] = None
    timezone: Optional[str] = None


class ApiKeyRequest(BaseModel):
    """Request model for adding an API key."""
    key_name: str
    key_value: str


@router.get("")
async def get_settings() -> Dict[str, Any]:
    """
    Get all application settings.
    
    Returns:
        Current settings configuration
    """
    settings = storage.get_settings()
    settings_dict = settings.to_dict()
    
    # Mask API keys for security
    settings_dict["api_keys"] = storage.get_api_keys()
    
    return {"settings": settings_dict}


@router.put("")
async def update_settings(request: UpdateSettingsRequest) -> Dict[str, Any]:
    """
    Update application settings.
    
    Args:
        request: Settings update parameters
    
    Returns:
        Updated settings
    """
    update_data = {k: v for k, v in request.dict().items() if v is not None}
    settings = storage.update_settings(**update_data)
    settings_dict = settings.to_dict()
    settings_dict["api_keys"] = storage.get_api_keys()
    
    return {
        "message": "Settings updated successfully",
        "settings": settings_dict
    }


@router.get("/api-keys")
async def get_api_keys() -> Dict[str, Any]:
    """
    Get all API keys (masked for security).
    
    Returns:
        Dictionary of API key names with masked values
    """
    return {
        "api_keys": storage.get_api_keys()
    }


@router.post("/api-keys")
async def add_api_key(request: ApiKeyRequest) -> Dict[str, Any]:
    """
    Add or update an API key.
    
    Args:
        request: API key details
    
    Returns:
        Confirmation message
    """
    if not request.key_name or not request.key_value:
        raise HTTPException(400, "Key name and value are required")
    
    storage.add_api_key(request.key_name, request.key_value)
    
    return {
        "message": f"API key '{request.key_name}' added successfully",
        "api_keys": storage.get_api_keys()
    }


@router.delete("/api-keys/{key_name}")
async def delete_api_key(key_name: str) -> Dict[str, Any]:
    """
    Delete an API key.
    
    Args:
        key_name: Name of the API key to delete
    
    Returns:
        Confirmation message
    """
    success = storage.remove_api_key(key_name)
    
    if not success:
        raise HTTPException(404, f"API key '{key_name}' not found")
    
    return {
        "message": f"API key '{key_name}' deleted successfully",
        "api_keys": storage.get_api_keys()
    }


@router.get("/themes")
async def get_available_themes() -> Dict[str, Any]:
    """
    Get available theme options.
    
    Returns:
        List of available themes
    """
    return {
        "themes": [
            {"id": "dark", "name": "Dark Mode", "preview": "#0A0A0F"},
            {"id": "light", "name": "Light Mode", "preview": "#FFFFFF"},
            {"id": "system", "name": "System Default", "preview": "auto"},
        ]
    }


@router.get("/languages")
async def get_available_languages() -> Dict[str, Any]:
    """
    Get available language options.
    
    Returns:
        List of available languages
    """
    return {
        "languages": [
            {"id": "en", "name": "English"},
            {"id": "es", "name": "Spanish"},
            {"id": "fr", "name": "French"},
            {"id": "de", "name": "German"},
            {"id": "ja", "name": "Japanese"},
            {"id": "zh", "name": "Chinese"},
        ]
    }
