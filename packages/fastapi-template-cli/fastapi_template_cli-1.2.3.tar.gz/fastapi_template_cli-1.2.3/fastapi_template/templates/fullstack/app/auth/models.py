"""
Unified FastAPI-Users models that adapt to the selected backend.
This file dynamically defines the user model based on the backend type.
"""

import uuid
from typing import Optional

from app.core.config import settings

if settings.BACKEND_TYPE == "sqlalchemy":
    # SQLAlchemy backend imports
    from app.db.database import Base
    from fastapi_users.db import SQLAlchemyBaseUserTable
    from sqlalchemy import Column, String
    from sqlalchemy.orm import relationship

    class User(SQLAlchemyBaseUserTable, Base):
        """User model for FastAPI-Users with SQLAlchemy."""

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

        # Add custom fields
        username = Column(String, unique=True, index=True, nullable=False)
        full_name = Column(String, nullable=True)

        # Relationships
        items = relationship(
            "Item", back_populates="owner", cascade="all, delete-orphan"
        )

elif settings.BACKEND_TYPE == "beanie":
    # Beanie/MongoDB backend imports
    from datetime import datetime

    from beanie import Document, Indexed
    from fastapi_users.db import BeanieUserDatabase
    from pydantic import Field

    class User(Document):
        """User model for FastAPI-Users with Beanie."""

        # FastAPI-Users fields
        id: uuid.UUID = Field(default_factory=uuid.uuid4)
        email: Indexed(str, unique=True)
        hashed_password: str
        is_active: bool = True
        is_superuser: bool = False
        is_verified: bool = False

        # Custom fields
        username: Indexed(str, unique=True)
        full_name: Optional[str] = None

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
        """Get user database for Beanie."""
        yield BeanieUserDatabase(User)

else:
    raise ValueError(f"Unsupported backend type: {settings.BACKEND_TYPE}")
