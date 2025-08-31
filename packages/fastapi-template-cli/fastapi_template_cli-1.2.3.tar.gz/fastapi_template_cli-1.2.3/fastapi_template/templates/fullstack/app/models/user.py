"""
User model supporting both SQLAlchemy and Beanie backends.
This module dynamically defines the User model based on the selected backend.
"""

import os
from datetime import datetime
from typing import TYPE_CHECKING, Optional

# Backend detection
BACKEND_TYPE = os.getenv("BACKEND_TYPE", "sqlalchemy")

if BACKEND_TYPE == "sqlalchemy":
    # SQLAlchemy model definition
    from app.db.database import Base
    from sqlalchemy import Boolean, Column, DateTime, Integer, String
    from sqlalchemy.orm import relationship

    if TYPE_CHECKING:
        pass

    class User(Base):
        """User model with authentication features (SQLAlchemy)."""

        __tablename__ = "users"

        id = Column(Integer, primary_key=True, index=True)
        email = Column(String, unique=True, index=True, nullable=False)
        username = Column(String, unique=True, index=True, nullable=False)
        full_name = Column(String, nullable=True)
        hashed_password = Column(String, nullable=False)
        is_active = Column(Boolean, default=True)
        is_superuser = Column(Boolean, default=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # Relationships
        items = relationship(
            "Item", back_populates="owner", cascade="all, delete-orphan"
        )

        def __repr__(self) -> str:
            return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"

elif BACKEND_TYPE == "beanie":
    # Beanie document model definition
    from beanie import Document
    from pydantic import EmailStr, Field

    class User(Document):
        """User document model (Beanie/MongoDB)."""

        email: EmailStr = Field(..., unique=True, index=True)
        username: str = Field(..., unique=True, index=True)
        full_name: Optional[str] = None
        hashed_password: str
        is_active: bool = Field(default=True)
        is_superuser: bool = Field(default=False)
        created_at: datetime = Field(default_factory=datetime.utcnow)
        updated_at: datetime = Field(default_factory=datetime.utcnow)

        class Settings:
            name = "users"
            indexes = ["email", "username", [("email", 1), ("username", 1)]]

        def __repr__(self) -> str:
            return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
