"""
Security Module

Provides authentication utilities including:
- Password hashing and verification
- JWT token creation and validation
- API key encryption and decryption
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import secrets
import base64
import logging

from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet

from app.config import settings

logger = logging.getLogger(__name__)

# Password hashing context with bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.bcrypt_rounds,
)

# Fernet cipher for API key encryption
_fernet: Optional[Fernet] = None


def _get_fernet() -> Fernet:
    """Get or create Fernet cipher for encryption."""
    global _fernet
    if _fernet is None:
        if settings.encryption_key:
            key = settings.encryption_key.encode()
            # Ensure key is 32 bytes, base64 encoded
            if len(key) != 44:  # Base64 encoded 32 bytes = 44 chars
                # Hash the key to get a proper length
                key = base64.urlsafe_b64encode(
                    hashlib.sha256(settings.encryption_key.encode()).digest()
                )
            _fernet = Fernet(key)
        else:
            # Generate a key for development (NOT for production!)
            logger.warning("No ENCRYPTION_KEY set, using generated key (NOT SECURE FOR PRODUCTION)")
            _fernet = Fernet(Fernet.generate_key())
    return _fernet


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The bcrypt hashed password to check against
        
    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The bcrypt hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary of claims to include in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
        "jti": secrets.token_urlsafe(16),  # Unique token ID
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> tuple[str, str, datetime]:
    """
    Create a JWT refresh token.
    
    Args:
        data: Dictionary of claims to include in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Tuple of (encoded token, token hash for storage, expiration datetime)
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    jti = secrets.token_urlsafe(32)  # Unique token ID
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": jti,
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    # Hash the token for secure storage
    token_hash = hashlib.sha256(encoded_jwt.encode()).hexdigest()
    
    return encoded_jwt, token_hash, expire


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token to verify
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        # Verify token type
        if payload.get("type") != token_type:
            logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
            return None
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None


def hash_token(token: str) -> str:
    """
    Create a hash of a token for secure storage.
    
    Args:
        token: The token to hash
        
    Returns:
        SHA-256 hash of the token
    """
    return hashlib.sha256(token.encode()).hexdigest()


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for secure storage.
    
    Args:
        api_key: The plain text API key
        
    Returns:
        Encrypted API key (base64 encoded)
    """
    fernet = _get_fernet()
    encrypted = fernet.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an encrypted API key.
    
    Args:
        encrypted_key: The encrypted API key (base64 encoded)
        
    Returns:
        The decrypted plain text API key
    """
    fernet = _get_fernet()
    decrypted = fernet.decrypt(encrypted_key.encode())
    return decrypted.decode()


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """
    Mask an API key for display purposes.
    
    Args:
        api_key: The API key to mask
        visible_chars: Number of visible characters at the end
        
    Returns:
        Masked API key (e.g., "****abcd")
    """
    if len(api_key) <= visible_chars:
        return "*" * len(api_key)
    return "*" * (len(api_key) - visible_chars) + api_key[-visible_chars:]


def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token.
    
    Args:
        email: User email for the reset token
        
    Returns:
        Encoded JWT token for password reset
    """
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {
        "sub": email,
        "exp": expire,
        "type": "password_reset",
        "jti": secrets.token_urlsafe(16),
    }
    
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token.
    
    Args:
        token: The password reset token to verify
        
    Returns:
        Email address if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        if payload.get("type") != "password_reset":
            return None
        
        return payload.get("sub")
        
    except JWTError:
        return None
