"""
Pydantic models for items.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    """Base item model with common attributes."""

    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(
        None, max_length=500, description="Item description"
    )
    price: float = Field(..., gt=0, description="Item price in USD")
    is_available: bool = Field(True, description="Whether the item is available")


class ItemCreate(ItemBase):
    """Model for creating new items."""

    pass


class ItemUpdate(BaseModel):
    """Model for updating existing items."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None


class Item(ItemBase):
    """Complete item model with ID."""

    id: UUID = Field(..., description="Unique item identifier")

    class Config:
        """Pydantic configuration."""

        orm_mode = True
