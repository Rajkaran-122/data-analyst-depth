"""
Settings Schemas

Pydantic models for user settings and API key management.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class SettingsUpdate(BaseModel):
    """Settings update request schema."""
    
    theme: Optional[str] = Field(None, pattern="^(dark|light|system)$")
    language: Optional[str] = Field(None, max_length=50)
    notifications_enabled: Optional[bool] = None
    auto_refresh: Optional[bool] = None
    refresh_interval: Optional[int] = Field(None, ge=10, le=3600)
    default_chart_type: Optional[str] = Field(None, pattern="^(bar|line|pie|area|scatter)$")
    timezone: Optional[str] = Field(None, max_length=100)
    
    @field_validator("refresh_interval")
    @classmethod
    def validate_refresh_interval(cls, v: Optional[int]) -> Optional[int]:
        """Validate refresh interval is reasonable."""
        if v is not None and (v < 10 or v > 3600):
            raise ValueError("Refresh interval must be between 10 and 3600 seconds")
        return v


class SettingsResponse(BaseModel):
    """Settings response schema."""
    
    theme: str = "dark"
    language: str = "en"
    notifications_enabled: bool = True
    auto_refresh: bool = True
    refresh_interval: int = 60
    default_chart_type: str = "bar"
    timezone: str = "UTC"
    api_keys: Dict[str, str] = {}  # key_name -> masked_value
    
    class Config:
        from_attributes = True


class ApiKeyCreate(BaseModel):
    """API key creation request schema."""
    
    key_name: str = Field(..., min_length=1, max_length=255)
    key_value: str = Field(..., min_length=1)
    
    @field_validator("key_name")
    @classmethod
    def validate_key_name(cls, v: str) -> str:
        """Validate and clean key name."""
        v = v.strip()
        if not v:
            raise ValueError("Key name cannot be empty")
        # Only allow alphanumeric, underscore, and hyphen
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Key name can only contain letters, numbers, underscores, and hyphens")
        return v


class ApiKeyResponse(BaseModel):
    """API key response schema (masked)."""
    
    key_name: str
    key_value: str  # Masked value (****XXXX)
    created_at: Optional[datetime] = None


class ApiKeyListResponse(BaseModel):
    """API key list response."""
    
    api_keys: List[ApiKeyResponse]


class ThemeOption(BaseModel):
    """Theme option for available themes."""
    
    id: str
    name: str
    preview_color: Optional[str] = None


class ThemeListResponse(BaseModel):
    """Available themes response."""
    
    themes: List[str] = ["dark", "light", "system"]


class LanguageOption(BaseModel):
    """Language option."""
    
    code: str
    name: str


class LanguageListResponse(BaseModel):
    """Available languages response."""
    
    languages: List[LanguageOption] = [
        LanguageOption(code="en", name="English"),
        LanguageOption(code="es", name="Spanish"),
        LanguageOption(code="fr", name="French"),
        LanguageOption(code="de", name="German"),
        LanguageOption(code="zh", name="Chinese"),
        LanguageOption(code="ja", name="Japanese"),
    ]
