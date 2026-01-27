"""
Settings API Routes (Production)

Backward-compatible user settings and API key management.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.settings_model import UserSettings, ApiKey
from app.models.activity import Activity
from app.api.deps import CurrentUser, OptionalUser
from app.services.cache_service import cache, CacheKeys
from app.core.security import encrypt_api_key, decrypt_api_key, mask_api_key
from app.core.exceptions import NotFoundError, ConflictError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["Settings"])


def _get_or_create_settings(db: Session, user_id: str) -> UserSettings:
    """Get or create user settings."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("")
async def get_settings(
    db: Session = Depends(get_db),
    current_user: Optional[object] = Depends(OptionalUser),
):
    """
    Get user settings including preferences and API keys.
    """
    if current_user:
        # Check cache
        cache_key = CacheKeys.user_settings(str(current_user.id))
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        settings = _get_or_create_settings(db, current_user.id)
        
        # Get API keys (masked)
        api_keys = db.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()
        api_keys_dict = {}
        for key in api_keys:
            try:
                decrypted = decrypt_api_key(key.key_value_encrypted)
                api_keys_dict[key.key_name] = mask_api_key(decrypted)
            except Exception:
                api_keys_dict[key.key_name] = "****invalid****"
        
        result = settings.to_dict(include_api_keys=True, api_keys=api_keys)
        result["api_keys"] = api_keys_dict
        
        # Cache for 5 minutes
        cache.set(cache_key, result, 300)
        
        return result
    
    # Demo settings
    return {
        "theme": "dark",
        "language": "en",
        "notifications_enabled": True,
        "auto_refresh": True,
        "refresh_interval": 60,
        "default_chart_type": "bar",
        "timezone": "UTC",
        "api_keys": {},
    }


@router.put("")
async def update_settings(
    theme: Optional[str] = None,
    language: Optional[str] = None,
    notifications_enabled: Optional[bool] = None,
    auto_refresh: Optional[bool] = None,
    refresh_interval: Optional[int] = None,
    default_chart_type: Optional[str] = None,
    timezone: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """
    Update user settings.
    """
    settings = _get_or_create_settings(db, current_user.id)
    
    # Update only provided fields
    if theme is not None and theme in ["dark", "light", "system"]:
        settings.theme = theme
    if language is not None:
        settings.language = language
    if notifications_enabled is not None:
        settings.notifications_enabled = notifications_enabled
    if auto_refresh is not None:
        settings.auto_refresh = auto_refresh
    if refresh_interval is not None and 10 <= refresh_interval <= 3600:
        settings.refresh_interval = refresh_interval
    if default_chart_type is not None:
        settings.default_chart_type = default_chart_type
    if timezone is not None:
        settings.timezone = timezone
    
    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)
    
    # Invalidate cache
    cache.delete(CacheKeys.user_settings(str(current_user.id)))
    
    # Get updated settings with API keys
    api_keys = db.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()
    api_keys_dict = {}
    for key in api_keys:
        try:
            decrypted = decrypt_api_key(key.key_value_encrypted)
            api_keys_dict[key.key_name] = mask_api_key(decrypted)
        except Exception:
            api_keys_dict[key.key_name] = "****invalid****"
    
    result = settings.to_dict()
    result["api_keys"] = api_keys_dict
    
    return result


@router.get("/api-keys")
async def list_api_keys(
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """
    List all API keys for the current user (masked values).
    """
    api_keys = db.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()
    
    result = []
    for key in api_keys:
        try:
            decrypted = decrypt_api_key(key.key_value_encrypted)
            masked = mask_api_key(decrypted)
        except Exception:
            masked = "****invalid****"
        
        result.append({
            "key_name": key.key_name,
            "key_value": masked,
            "created_at": key.created_at.isoformat() if key.created_at else None,
        })
    
    return {"api_keys": result}


@router.post("/api-keys")
async def add_api_key(
    key_name: str,
    key_value: str,
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """
    Add or update an API key.
    """
    # Check if key already exists
    existing = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.key_name == key_name
    ).first()
    
    encrypted_value = encrypt_api_key(key_value)
    
    if existing:
        # Update existing key
        existing.key_value_encrypted = encrypted_value
        existing.updated_at = datetime.utcnow()
        db.commit()
        message = f"API key '{key_name}' updated successfully"
    else:
        # Create new key
        api_key = ApiKey(
            user_id=current_user.id,
            key_name=key_name,
            key_value_encrypted=encrypted_value,
        )
        db.add(api_key)
        db.commit()
        message = f"API key '{key_name}' added successfully"
    
    # Invalidate cache
    cache.delete(CacheKeys.user_settings(str(current_user.id)))
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        activity_type="settings",
        title=f"API key configured: {key_name}",
        status="success",
    )
    db.add(activity)
    db.commit()
    
    return {
        "message": message,
        "key_name": key_name,
        "key_value": mask_api_key(key_value),
    }


@router.delete("/api-keys/{key_name}")
async def delete_api_key(
    key_name: str,
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """
    Delete an API key.
    """
    api_key = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.key_name == key_name
    ).first()
    
    if not api_key:
        raise NotFoundError(
            message=f"API key '{key_name}' not found",
            resource_type="api_key",
            resource_id=key_name,
        )
    
    db.delete(api_key)
    db.commit()
    
    # Invalidate cache
    cache.delete(CacheKeys.user_settings(str(current_user.id)))
    
    return {"message": f"API key '{key_name}' deleted successfully"}


@router.get("/themes")
async def get_available_themes():
    """
    Get list of available themes.
    """
    return {
        "themes": [
            {"id": "dark", "name": "Dark Mode", "preview_color": "#1F2937"},
            {"id": "light", "name": "Light Mode", "preview_color": "#FFFFFF"},
            {"id": "system", "name": "System Default", "preview_color": "#6B7280"},
        ]
    }


@router.get("/languages")
async def get_available_languages():
    """
    Get list of available languages.
    """
    return {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "zh", "name": "Chinese"},
            {"code": "ja", "name": "Japanese"},
            {"code": "hi", "name": "Hindi"},
        ]
    }


@router.post("/reset")
async def reset_settings(
    db: Session = Depends(get_db),
    current_user: object = Depends(CurrentUser),
):
    """
    Reset settings to defaults.
    """
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if settings:
        settings.theme = "dark"
        settings.language = "en"
        settings.notifications_enabled = True
        settings.auto_refresh = True
        settings.refresh_interval = 60
        settings.default_chart_type = "bar"
        settings.timezone = "UTC"
        settings.updated_at = datetime.utcnow()
        db.commit()
    
    # Invalidate cache
    cache.delete(CacheKeys.user_settings(str(current_user.id)))
    
    return {"message": "Settings reset to defaults"}
