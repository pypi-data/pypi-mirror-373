"""
Unified FastAPI-Users manager and configuration that adapts to the selected backend.
This file dynamically imports and configures based on the backend type.
"""

import uuid
from typing import Optional

# Dynamic backend imports
from app.core.config import settings
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

# Backend-specific imports will be determined at runtime
if settings.BACKEND_TYPE == "sqlalchemy":
    from app.auth.models import User as UserModel
    from app.db.database import async_session_maker
    from fastapi_users.db import SQLAlchemyUserDatabase
    from sqlalchemy.ext.asyncio import AsyncSession

    async def get_user_db(session: AsyncSession = Depends(async_session_maker)):
        """Get user database for SQLAlchemy."""
        yield SQLAlchemyUserDatabase(session, UserModel)

elif settings.BACKEND_TYPE == "beanie":
    from app.auth.models import User as UserModel
    from app.auth.models import get_user_db as get_user_db_raw

    async def get_user_db():
        """Get user database for Beanie."""
        async for db in get_user_db_raw():
            yield db

else:
    raise ValueError(f"Unsupported backend type: {settings.BACKEND_TYPE}")


class UserManager(UUIDIDMixin, BaseUserManager[UserModel, uuid.UUID]):
    """User manager for FastAPI-Users - unified for both backends."""

    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(
        self, user: UserModel, request: Optional[Request] = None
    ):
        """Called after user registration."""
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: UserModel, token: str, request: Optional[Request] = None
    ):
        """Called after forgot password request."""
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserModel, token: str, request: Optional[Request] = None
    ):
        """Called after verification request."""
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    """Get user manager - unified for both backends."""
    yield UserManager(user_db)


# Authentication configuration - unified for both backends
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    """Get JWT strategy for authentication."""
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# Create authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# Create FastAPI-Users instance - unified for both backends
fastapi_users = FastAPIUsers[UserModel, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Current user dependency - unified for both backends
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
