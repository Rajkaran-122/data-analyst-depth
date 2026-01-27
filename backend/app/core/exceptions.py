"""
Custom Exceptions Module

Defines application-specific exceptions with proper HTTP status codes.
"""

from typing import Optional, Dict, Any


class AppException(Exception):
    """
    Base exception for all application errors.
    
    Attributes:
        code: Error code string for programmatic handling
        message: Human-readable error message
        status_code: HTTP status code to return
        details: Additional error details
    """
    
    def __init__(
        self,
        code: str = "INTERNAL_ERROR",
        message: str = "An unexpected error occurred",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class AuthenticationError(AppException):
    """Raised when authentication fails."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTH_001",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=401,
            details=details
        )


class AuthorizationError(AppException):
    """Raised when user lacks required permissions."""
    
    def __init__(
        self,
        message: str = "You don't have permission to access this resource",
        code: str = "AUTH_004",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=403,
            details=details
        )


class NotFoundError(AppException):
    """Raised when a resource is not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "RES_001",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if resource_type:
            error_details["resource_type"] = resource_type
        if resource_id:
            error_details["resource_id"] = resource_id
        
        super().__init__(
            code=code,
            message=message,
            status_code=404,
            details=error_details
        )


class ValidationError(AppException):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        code: str = "VAL_001",
        errors: Optional[list] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if errors:
            error_details["errors"] = errors
        
        super().__init__(
            code=code,
            message=message,
            status_code=422,
            details=error_details
        )


class ConflictError(AppException):
    """Raised when there's a resource conflict (e.g., duplicate email)."""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        code: str = "RES_002",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=409,
            details=details
        )


class RateLimitError(AppException):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Too many requests. Please try again later.",
        code: str = "RATE_001",
        limit: Optional[int] = None,
        remaining: int = 0,
        reset_at: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if limit:
            error_details["limit"] = limit
        error_details["remaining"] = remaining
        if reset_at:
            error_details["reset"] = reset_at
        
        super().__init__(
            code=code,
            message=message,
            status_code=429,
            details=error_details
        )


class ExternalAPIError(AppException):
    """Raised when an external API call fails."""
    
    def __init__(
        self,
        message: str = "External service error",
        code: str = "EXT_001",
        service: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if service:
            error_details["service"] = service
        
        super().__init__(
            code=code,
            message=message,
            status_code=503,
            details=error_details
        )


class FileUploadError(AppException):
    """Raised when file upload fails."""
    
    def __init__(
        self,
        message: str = "File upload failed",
        code: str = "VAL_002",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=400,
            details=details
        )


class FileTooLargeError(AppException):
    """Raised when uploaded file exceeds size limit."""
    
    def __init__(
        self,
        message: str = "File too large",
        code: str = "VAL_003",
        max_size: Optional[int] = None,
        actual_size: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if max_size:
            error_details["max_size"] = max_size
        if actual_size:
            error_details["actual_size"] = actual_size
        
        super().__init__(
            code=code,
            message=message,
            status_code=413,
            details=error_details
        )


class DatabaseError(AppException):
    """Raised when a database operation fails."""
    
    def __init__(
        self,
        message: str = "Database error",
        code: str = "SYS_003",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=500,
            details=details
        )
