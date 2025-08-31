"""
Item model supporting both SQLAlchemy and Beanie backends.
This module dynamically defines the Item model based on the selected backend.
"""

import os
from datetime import datetime
from typing import TYPE_CHECKING, Optional

# Backend detection
BACKEND_TYPE = os.getenv("BACKEND_TYPE", "sqlalchemy")

if BACKEND_TYPE == "sqlalchemy":
    # SQLAlchemy model definition
    from app.db.database import Base
    from sqlalchemy import (
        Boolean,
        Column,
        DateTime,
        ForeignKey,
        Integer,
        Numeric,
        String,
        Text,
    )
    from sqlalchemy.orm import relationship

    if TYPE_CHECKING:
        from app.models.user import User

    class Item(Base):
        """Item model with user relationship (SQLAlchemy)."""

        __tablename__ = "items"

        id = Column(Integer, primary_key=True, index=True)
        title = Column(String, index=True, nullable=False)
        description = Column(Text, nullable=True)
        price = Column(Numeric(10, 2), nullable=False)
        is_available = Column(Boolean, default=True)
        owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # Relationships
        owner = relationship("User", back_populates="items")

        def __repr__(self) -> str:
            return f"<Item(id={self.id}, title='{self.title}', price={self.price}, owner_id={self.owner_id})>"

elif BACKEND_TYPE == "beanie":
    # Beanie document model definition
    from app.models.user import User
    from beanie import Document, Link
    from pydantic import Field

    class Item(Document):
        """Item document model (Beanie/MongoDB)."""

        title: str = Field(..., index=True)
        description: Optional[str] = None
        price: float = Field(..., gt=0)
        is_available: bool = Field(default=True)
        owner_id: Link[User]  # Reference to User document
        created_at: datetime = Field(default_factory=datetime.utcnow)
        updated_at: datetime = Field(default_factory=datetime.utcnow)

        class Settings:
            name = "items"
            indexes = ["title", [("owner_id", 1)]]

        def __repr__(self) -> str:
            return f"<Item(id={self.id}, title='{self.title}', price={self.price}, owner_id={self.owner_id})"
