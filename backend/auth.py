"""
Authentication & Authorization module for Data Analyst Depth.

Provides:
- Password hashing (bcrypt via passlib)
- JWT access & refresh token creation / validation
- FastAPI dependencies: get_current_user, require_admin
- Auth routes: register, login, refresh, logout, forgot/reset password
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
import os
import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request  # type: ignore
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # type: ignore
from pydantic import BaseModel, EmailStr, Field  # type: ignore
from passlib.context import CryptContext  # type: ignore
from jose import JWTError, jwt  # type: ignore


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "data-analyst-depth-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---------------------------------------------------------------------------
# In-memory user store  (will be migrated to MongoDB in a future sprint)
# ---------------------------------------------------------------------------

_users_db: Dict[str, Dict[str, Any]] = {}         # email -> user dict
_blacklisted_tokens: set = set()                   # revoked refresh tokens


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _seed_admin():
    """Create a default admin account if none exists."""
    admin_email = "admin@dataanalyst.com"
    if admin_email not in _users_db:
        _users_db[admin_email] = {
            "id": str(uuid.uuid4()),
            "name": "Admin",
            "email": admin_email,
            "hashed_password": pwd_context.hash("Admin@123"),
            "role": "admin",
            "status": "active",
            "created_at": _now_iso(),
            "last_login": None,
        }
        logger.info(f"Default admin account created: {admin_email} / Admin@123")


_seed_admin()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    status: str
    created_at: str
    last_login: Optional[str] = None


class UpdateUserRoleRequest(BaseModel):
    role: str = Field(..., pattern="^(admin|user)$")


class UpdateUserStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(active|inactive)$")


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def _create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + expires_delta
    to_encode["iat"] = datetime.now(timezone.utc)
    to_encode["jti"] = str(uuid.uuid4())  # unique token id
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: str, email: str, role: str) -> str:
    return _create_token(
        {"sub": user_id, "email": email, "role": role, "type": "access"},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str, email: str) -> str:
    return _create_token(
        {"sub": user_id, "email": email, "type": "refresh"},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token. Raises HTTPException on failure."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
        )


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

def _validate_password_strength(password: str) -> Optional[str]:
    """Return an error message if the password is too weak, else None."""
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter."
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one number."
    if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
        return "Password must contain at least one special character."
    return None


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """Dependency that extracts and validates the current user from the JWT."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
        )
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Access token required.",
        )
    email = str(payload.get("email", ""))
    user = _users_db.get(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    if user.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact an administrator.",
        )
    return user


async def require_admin(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency that requires the current user to have admin role."""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return user


# ---------------------------------------------------------------------------
# Auth Routes
# ---------------------------------------------------------------------------

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest):
    """Register a new user account."""
    # Check email uniqueness
    if req.email.lower() in _users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    # Validate password strength
    pw_error = _validate_password_strength(req.password)
    if pw_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=pw_error)

    user_id = str(uuid.uuid4())
    now = _now_iso()
    user = {
        "id": user_id,
        "name": req.name,
        "email": req.email.lower(),
        "hashed_password": pwd_context.hash(req.password),
        "role": "user",
        "status": "active",
        "created_at": now,
        "last_login": now,
    }
    _users_db[req.email.lower()] = user

    access = create_access_token(user_id, user["email"], user["role"])
    refresh = create_refresh_token(user_id, user["email"])

    logger.info(f"New user registered: {user['email']}")
    return TokenResponse(  # type: ignore
        access_token=access,  # type: ignore
        refresh_token=refresh,  # type: ignore
        user={k: v for k, v in user.items() if k != "hashed_password"},  # type: ignore
    )




@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Authenticate a user and return tokens."""
    user = _users_db.get(req.email.lower())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    
    hashed_pw = user.get("hashed_password", "")
    if not pwd_context.verify(req.password, str(hashed_pw)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    
    if user.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact an administrator.",
        )

    user["last_login"] = _now_iso()
    uid = str(user.get("id", ""))
    u_email = str(user.get("email", ""))
    u_role = str(user.get("role", ""))
    
    access = create_access_token(uid, u_email, u_role)
    refresh = create_refresh_token(uid, u_email)

    logger.info(f"User logged in: {u_email}")
    return TokenResponse(  # type: ignore
        access_token=str(access),  # type: ignore
        refresh_token=str(refresh),  # type: ignore
        user={k: v for k, v in user.items() if k != "hashed_password"},  # type: ignore
    )




@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: RefreshRequest):
    """Refresh an access token using a valid refresh token."""
    if req.refresh_token in _blacklisted_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked.",
        )
    payload = decode_token(req.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Refresh token required.",
        )
    email_val = payload.get("email")
    email = str(email_val) if email_val is not None else ""
    user = _users_db.get(email)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    # Blacklist old refresh token (rotation)
    _blacklisted_tokens.add(req.refresh_token)

    access = create_access_token(user["id"], user["email"], user["role"])
    refresh = create_refresh_token(user["id"], user["email"])

    return TokenResponse(  # type: ignore
        access_token=access,  # type: ignore
        refresh_token=refresh,  # type: ignore
        user={k: v for k, v in user.items() if k != "hashed_password"},  # type: ignore
    )




@router.post("/logout", response_model=MessageResponse)
async def logout(req: RefreshRequest):
    """Log out by blacklisting the refresh token."""
    _blacklisted_tokens.add(req.refresh_token)
    logger.info("User logged out, refresh token revoked.")
    return MessageResponse(message="Logged out successfully.")  # type: ignore



@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(req: ForgotPasswordRequest):
    """Request a password reset. Returns a token (in production, emailed)."""
    user = _users_db.get(req.email.lower())
    if not user:
        # Don't reveal whether the email exists
        return MessageResponse(message="If an account with that email exists, a reset link has been sent.")  # type: ignore


    reset_token = _create_token(
        {"sub": user["id"], "email": user["email"], "type": "reset"},
        timedelta(hours=1),
    )
    # In production: send an email with the reset link
    reset_token_str = str(reset_token)
    logger.info(f"Password reset token generated for {user['email']}: {reset_token_str[0:20]}...")  # type: ignore


    return MessageResponse(message="If an account with that email exists, a reset link has been sent.")  # type: ignore



@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(req: ResetPasswordRequest):
    """Reset password using a valid reset token."""
    payload = decode_token(req.token)
    if payload.get("type") != "reset":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token.")

    email_val = payload.get("email")
    email = str(email_val) if email_val is not None else ""
    user = _users_db.get(email)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    pw_error = _validate_password_strength(req.new_password)
    if pw_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=pw_error)

    user["hashed_password"] = pwd_context.hash(req.new_password)
    logger.info(f"Password reset for {email}")
    return MessageResponse(message="Password has been reset successfully.")  # type: ignore



@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    req: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Change password for an authenticated user."""
    if not pwd_context.verify(req.current_password, current_user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect.")

    pw_error = _validate_password_strength(req.new_password)
    if pw_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=pw_error)

    current_user["hashed_password"] = pwd_context.hash(req.new_password)
    logger.info(f"Password changed for {current_user['email']}")
    return MessageResponse(message="Password changed successfully.")  # type: ignore



# ---------------------------------------------------------------------------
# Profile route
# ---------------------------------------------------------------------------

@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get the current user's profile."""
    return UserResponse(**{k: v for k, v in current_user.items() if k != "hashed_password"})


# ---------------------------------------------------------------------------
# Admin: User Management Routes
# ---------------------------------------------------------------------------

@router.get("/admin/users", response_model=List[UserResponse])
async def list_users(admin: Dict[str, Any] = Depends(require_admin)):
    """List all users (admin only)."""
    return [
        UserResponse(**{k: v for k, v in u.items() if k != "hashed_password"})
        for u in _users_db.values()
    ]


@router.patch("/admin/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    req: UpdateUserRoleRequest,
    admin: Dict[str, Any] = Depends(require_admin),
):
    """Change a user's role (admin only)."""
    target = next((u for u in _users_db.values() if u["id"] == user_id), None)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    target["role"] = req.role
    logger.info(f"Admin {admin['email']} changed role of {target['email']} to {req.role}")
    return UserResponse(**{k: v for k, v in target.items() if k != "hashed_password"})


@router.patch("/admin/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: str,
    req: UpdateUserStatusRequest,
    admin: Dict[str, Any] = Depends(require_admin),
):
    """Activate or deactivate a user account (admin only)."""
    target = next((u for u in _users_db.values() if u["id"] == user_id), None)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    target["status"] = req.status
    logger.info(f"Admin {admin['email']} changed status of {target['email']} to {req.status}")
    return UserResponse(**{k: v for k, v in target.items() if k != "hashed_password"})
