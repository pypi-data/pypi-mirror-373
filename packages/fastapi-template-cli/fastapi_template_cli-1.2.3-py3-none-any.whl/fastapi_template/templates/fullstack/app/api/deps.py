"""
API dependencies for authentication and authorization.
"""

from app.core import security
from app.crud.user import user as crud_user
from app.db.database import get_db
from app.models.user import User
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

security = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(security)
) -> User:
    """
    Get current authenticated user.

    Args:
        db: Database session
        token: JWT token

    Returns:
        Current user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = security.verify_token(token.credentials)
    user = crud_user.get(db, id=token_data)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current user

    Returns:
        Active user
    """
    if not crud_user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active superuser.

    Args:
        current_user: Current user

    Returns:
        Superuser
    """
    if not crud_user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return current_user
