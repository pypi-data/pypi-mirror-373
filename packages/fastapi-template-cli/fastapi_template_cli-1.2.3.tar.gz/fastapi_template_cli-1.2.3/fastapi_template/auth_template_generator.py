"""
Dynamic authentication template generator for FastAPI template CLI.

This module provides backend-specific authentication file generation without hardcoded conditions.
It uses a modular approach to generate models.py and manager.py files based on the selected backend.
"""

import textwrap
from typing import Any, Dict


class AuthTemplateGenerator:
    """Generates backend-specific authentication templates dynamically."""

    def __init__(self, backend_type: str):
        """Initialize the generator with backend type."""
        self.backend_type = backend_type.lower()
        self._validate_backend()

    def _validate_backend(self) -> None:
        """Validate the backend type."""
        valid_backends = {"sqlalchemy", "beanie"}
        if self.backend_type not in valid_backends:
            raise ValueError(f"Unsupported backend type: {self.backend_type}")

    def generate_models_file(self, custom_fields: Dict[str, Any] = None) -> str:
        """Generate the models.py file based on the selected backend."""
        if self.backend_type == "sqlalchemy":
            return self._generate_sqlalchemy_models(custom_fields)
        elif self.backend_type == "beanie":
            return self._generate_beanie_models(custom_fields)

    def generate_manager_file(self) -> str:
        """Generate the manager.py file based on the selected backend."""
        if self.backend_type == "sqlalchemy":
            return self._generate_sqlalchemy_manager()
        elif self.backend_type == "beanie":
            return self._generate_beanie_manager()

    def _generate_sqlalchemy_models(self, custom_fields: Dict[str, Any] = None) -> str:
        """Generate SQLAlchemy-specific user model."""
        default_fields = {
            "username": {
                "type": "String",
                "unique": True,
                "index": True,
                "nullable": False,
            },
            "full_name": {"type": "String", "nullable": True},
        }

        if custom_fields:
            default_fields.update(custom_fields)

        field_definitions = []
        for field_name, config in default_fields.items():
            field_def = f"    {field_name} = Column({config['type']}"
            if config.get("unique"):
                field_def += ", unique=True"
            if config.get("index"):
                field_def += ", index=True"
            if "nullable" in config:
                field_def += f", nullable={config['nullable']}"
            field_def += ")"
            field_definitions.append(field_def)

        fields_str = "\n".join(field_definitions)

        return textwrap.dedent(
            f"""
        \"\"\"User model for FastAPI-Users with SQLAlchemy backend.
        This file is generated specifically for SQLAlchemy ORM.\"\"\"

        import uuid
        from sqlalchemy import Column, String, Boolean, DateTime
        from sqlalchemy.orm import relationship
        from sqlalchemy.sql import func
        from fastapi_users.db import SQLAlchemyBaseUserTable
        from app.db.database import Base


        class User(SQLAlchemyBaseUserTable, Base):
            \"\"\"User model for FastAPI-Users with SQLAlchemy.\"\"\"
            
            __tablename__ = "users"
            
            # FastAPI-Users already provides:
            # - id (UUID)
            # - email (str)
            # - hashed_password (str)
            # - is_active (bool)
            # - is_superuser (bool)
            # - is_verified (bool)
            # - created_at (DateTime)
            # - updated_at (DateTime)
            
            # Custom fields
        {fields_str}
            
            # Relationships
            items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    """
        )

    def _generate_beanie_models(self, custom_fields: Dict[str, Any] = None) -> str:
        """Generate Beanie-specific user model."""
        default_fields = {
            "username": {"type": "Indexed(str, unique=True)", "required": True},
            "full_name": {"type": "Optional[str]", "default": "None"},
        }

        if custom_fields:
            default_fields.update(custom_fields)

        field_definitions = []
        for field_name, config in default_fields.items():
            field_def = f"    {field_name}: {config['type']}"
            if "default" in config:
                field_def += f" = {config['default']}"
            field_definitions.append(field_def)

        fields_str = "\n".join(field_definitions)

        return textwrap.dedent(
            f"""
        \"\"\"User model for FastAPI-Users with Beanie backend.
        This file is generated specifically for Beanie ODM with MongoDB.\"\"\"

        import uuid
        from typing import Optional
        from beanie import Document, Indexed
        from pydantic import Field
        from datetime import datetime
        from fastapi_users.db import BeanieUserDatabase


        class User(Document):
            \"\"\"User model for FastAPI-Users with Beanie.\"\"\"
            
            # FastAPI-Users fields
            id: uuid.UUID = Field(default_factory=uuid.uuid4)
            email: Indexed(str, unique=True)
            hashed_password: str
            is_active: bool = True
            is_superuser: bool = False
            is_verified: bool = False
            
            # Custom fields
        {fields_str}
            
            # Timestamps
            created_at: datetime = Field(default_factory=datetime.utcnow)
            updated_at: datetime = Field(default_factory=datetime.utcnow)
            
            class Settings:
                name = "users"
                indexes = [
                    "email",
                    "username",
                ]


        async def get_user_db():
            \"\"\"Get user database for Beanie.\"\"\"
            yield BeanieUserDatabase(User)
    """
        )

    def _generate_sqlalchemy_manager(self) -> str:
        """Generate SQLAlchemy-specific manager configuration."""
        return textwrap.dedent(
            """
        \"\"\"FastAPI-Users manager and configuration for SQLAlchemy backend.
        This file is generated specifically for SQLAlchemy ORM.\"\"\"

        import uuid
        from typing import Optional

        from fastapi import Depends, Request
        from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
        from fastapi_users.authentication import (
            AuthenticationBackend,
            BearerTransport,
            JWTStrategy,
        )
        from fastapi_users.db import SQLAlchemyUserDatabase
        from sqlalchemy.ext.asyncio import AsyncSession

        from app.core.config import settings
        from app.db.database import async_session_maker
        from app.auth.models import User as UserModel


        async def get_user_db(session: AsyncSession = Depends(async_session_maker)):
            \"\"\"Get user database for SQLAlchemy.\"\"\"
            yield SQLAlchemyUserDatabase(session, UserModel)


        class UserManager(UUIDIDMixin, BaseUserManager[UserModel, uuid.UUID]):
            \"\"\"User manager for FastAPI-Users with SQLAlchemy.\"\"\"
            
            reset_password_token_secret = settings.SECRET_KEY
            verification_token_secret = settings.SECRET_KEY
            
            async def on_after_register(self, user: UserModel, request: Optional[Request] = None):
                \"\"\"Called after user registration.\"\"\"
                print(f"User {user.id} has registered.")
            
            async def on_after_forgot_password(
                self, user: UserModel, token: str, request: Optional[Request] = None
            ):
                \"\"\"Called after forgot password request.\"\"\"
                print(f"User {user.id} has forgot their password. Reset token: {token}")
            
            async def on_after_request_verify(
                self, user: UserModel, token: str, request: Optional[Request] = None
            ):
                \"\"\"Called after verification request.\"\"\"
                print(f"Verification requested for user {user.id}. Verification token: {token}")


        async def get_user_manager(user_db=Depends(get_user_db)):
            \"\"\"Get user manager.\"\"\"
            yield UserManager(user_db)


        # Authentication configuration
        bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


        def get_jwt_strategy() -> JWTStrategy:
            \"\"\"Get JWT strategy for authentication.\"\"\"
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

        # Create FastAPI-Users instance
        fastapi_users = FastAPIUsers[UserModel, uuid.UUID](
            get_user_manager,
            [auth_backend],
        )

        # Current user dependency
        current_active_user = fastapi_users.current_user(active=True)
        current_superuser = fastapi_users.current_user(active=True, superuser=True)
    """
        )

    def _generate_beanie_manager(self) -> str:
        """Generate Beanie-specific manager configuration."""
        return textwrap.dedent(
            """
        \"\"\"FastAPI-Users manager and configuration for Beanie backend.
        This file is generated specifically for Beanie ODM with MongoDB.\"\"\"

        import uuid
        from typing import Optional

        from fastapi import Depends, Request
        from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
        from fastapi_users.authentication import (
            AuthenticationBackend,
            BearerTransport,
            JWTStrategy,
        )
        from fastapi_users.db import BeanieUserDatabase

        from app.core.config import settings
        from app.auth.models import User as UserModel, get_user_db as get_user_db_raw


        async def get_user_db():
            \"\"\"Get user database for Beanie.\"\"\"
            async for db in get_user_db_raw():
                yield db


        class UserManager(UUIDIDMixin, BaseUserManager[UserModel, uuid.UUID]):
            \"\"\"User manager for FastAPI-Users with Beanie.\"\"\"
            
            reset_password_token_secret = settings.SECRET_KEY
            verification_token_secret = settings.SECRET_KEY
            
            async def on_after_register(self, user: UserModel, request: Optional[Request] = None):
                \"\"\"Called after user registration.\"\"\"
                print(f"User {user.id} has registered.")
            
            async def on_after_forgot_password(
                self, user: UserModel, token: str, request: Optional[Request] = None
            ):
                \"\"\"Called after forgot password request.\"\"\"
                print(f"User {user.id} has forgot their password. Reset token: {token}")
            
            async def on_after_request_verify(
                self, user: UserModel, token: str, request: Optional[Request] = None
            ):
                \"\"\"Called after verification request.\"\"\"
                print(f"Verification requested for user {user.id}. Verification token: {token}")


            async def get_user_manager(user_db=Depends(get_user_db)):
                \"\"\"Get user manager.\"\"\"
                yield UserManager(user_db)


            # Authentication configuration
            bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


            def get_jwt_strategy() -> JWTStrategy:
                \"\"\"Get JWT strategy for authentication.\"\"\"
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

            # Create FastAPI-Users instance
            fastapi_users = FastAPIUsers[UserModel, uuid.UUID](
                get_user_manager,
                [auth_backend],
            )

            # Current user dependency
            current_active_user = fastapi_users.current_user(active=True)
            current_superuser = fastapi_users.current_user(active=True, superuser=True)
        """
        )

    def generate_config_file(self) -> str:
        """Generate the auth config.py file."""
        return textwrap.dedent(
            """
        \"\"\"Authentication configuration for FastAPI-Users.
        This file contains common authentication settings.\"\"\"

        from fastapi_users import models
        from pydantic import BaseModel
        from typing import Optional


        class UserCreate(BaseModel):
            \"\"\"User creation schema.\"\"\"
            email: str
            password: str
            username: str
            full_name: Optional[str] = None

        class UserUpdate(BaseModel):
            \"\"\"User update schema.\"\"\"
            email: Optional[str] = None
            password: Optional[str] = None
            username: Optional[str] = None
            full_name: Optional[str] = None

        class UserRead(BaseModel):
            \"\"\"User read schema.\"\"\"
            id: str
            email: str
            username: str
            full_name: Optional[str] = None
            is_active: bool
            is_superuser: bool
            is_verified: bool
        """
        )
