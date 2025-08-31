"""
Database configuration and session management (async).
This module dynamically configures the database backend based on the selected template.
Supports both SQLAlchemy (PostgreSQL) and Beanie (MongoDB) backends.
"""

import os
from typing import Any, AsyncGenerator

# Backend detection based on environment variable set during template creation
BACKEND_TYPE = os.getenv("BACKEND_TYPE", "sqlalchemy")

if BACKEND_TYPE == "sqlalchemy":
    # SQLAlchemy + PostgreSQL configuration
    from app.core.config import settings
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )
    from sqlalchemy.orm import declarative_base

    # Create async database engine
    engine = create_async_engine(
        str(settings.SQLALCHEMY_DATABASE_URI).replace(
            "postgresql://", "postgresql+asyncpg://"
        ),
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
    )

    # Create async session factory
    SessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
        class_=AsyncSession,
    )

    # Create base class for models
    Base = declarative_base()

    async def get_db() -> AsyncGenerator[AsyncSession, None]:
        """
        Async database dependency for FastAPI (SQLAlchemy).

        Yields:
            Async database session
        """
        async with SessionLocal() as session:
            yield session

elif BACKEND_TYPE == "beanie":
    # Beanie + MongoDB configuration
    from app.core.config import settings
    from beanie import init_beanie
    from motor.motor_asyncio import AsyncIOMotorClient

    # Create MongoDB client
    client = AsyncIOMotorClient(settings.MONGODB_DATABASE_URI)

    # Get database reference
    database = client[settings.MONGODB_DATABASE_NAME]

    async def init_database():
        """Initialize Beanie with document models."""
        from app.models.item import Item
        from app.models.user import User

        await init_beanie(
            database=database,
            document_models=[
                User,
                Item,
            ],
        )

    async def get_db() -> AsyncGenerator[Any, None]:
        """
        Async database dependency for FastAPI (Beanie).

        Yields:
            MongoDB database instance
        """
        yield database

else:
    raise ValueError(f"Unsupported backend type: {BACKEND_TYPE}")
