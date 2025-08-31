"""
Security utilities for authentication and authorization.
"""

from datetime import datetime, timedelta
from typing import Any, Union

from app.core.config import settings
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from passlib.context import CryptContext
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Import user models based on backend type
try:
    # Try FastAPI-Users SQLAlchemy model first
    from app.auth.models import User as SQLUser
    from app.crud.user import user as crud_user

    USE_SQLALCHEMY = True
except ImportError:
    USE_SQLALCHEMY = False
    SQLUser = None
    crud_user = None

try:
    # Try FastAPI-Users Beanie model
    from app.auth.models_beanie import User as BeanieUser
    from beanie import PydanticObjectId

    USE_BEANIE = True
except ImportError:
    USE_BEANIE = False
    BeanieUser = None
    PydanticObjectId = None

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT security scheme
security = HTTPBearer()


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: The subject of the token (usually user ID)
        expires_delta: Token expiration time

    Returns:
        JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password
        hashed_password: The hashed password

    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: The plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_token(token: str) -> str:
    """
    Verify a JWT token and return the subject.

    Args:
        token: JWT token string

    Returns:
        Subject (user ID) from the token

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject: str = payload.get("sub")
        if subject is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return subject
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """
    Get the current user from JWT token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        User ID from the token
    """
    token = credentials.credentials
    return verify_token(token)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self';"
        )
        response.headers["Content-Security-Policy"] = csp

        return response


def setup_security_headers(app):
    """Setup security headers middleware for the FastAPI app."""
    app.add_middleware(SecurityHeadersMiddleware)


async def get_current_user_from_db(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Union[SQLUser, BeanieUser]:
    """
    Get the current user from JWT token and fetch from database.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        User model instance from database

    Raises:
        HTTPException: If user not found or token invalid
    """
    token = credentials.credentials
    user_id = verify_token(token)

    if USE_SQLALCHEMY and SQLUser:
        # SQLAlchemy backend
        from app.db.database import async_session_maker

        async with async_session_maker() as session:
            from sqlalchemy import select

            result = await session.execute(
                select(SQLUser).where(SQLUser.id == int(user_id))
            )
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user

    elif USE_BEANIE and BeanieUser:
        # Beanie/MongoDB backend
        try:
            from beanie import PydanticObjectId

            user = await BeanieUser.get(PydanticObjectId(user_id))
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except Exception:
            raise HTTPException(status_code=404, detail="User not found")

    else:
        # Fallback to legacy behavior
        raise HTTPException(
            status_code=500, detail="No user database backend configured"
        )


async def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Union[SQLUser, BeanieUser]:
    """
    Get current active user from database.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Active user model instance

    Raises:
        HTTPException: If user is inactive or not found
    """
    user = await get_current_user_from_db(credentials)

    if hasattr(user, "is_active") and not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


async def get_current_active_superuser(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Union[SQLUser, BeanieUser]:
    """
    Get current active superuser from database.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Superuser model instance

    Raises:
        HTTPException: If user is not a superuser or not found
    """
    user = await get_current_user_from_db(credentials)

    if hasattr(user, "is_active") and not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    if hasattr(user, "is_superuser") and not user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    return user
