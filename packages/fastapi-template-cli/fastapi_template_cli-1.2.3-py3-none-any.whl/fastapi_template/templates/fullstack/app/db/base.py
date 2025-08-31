"""
Base model for all database models.
"""

from app.db.database import Base  # noqa: F401
from app.models.item import Item  # noqa: F401

# Import all models here for Alembic
from app.models.user import User  # noqa: F401
