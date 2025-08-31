"""
Main FastAPI application for Full-stack template.
Production-ready FastAPI application with unified backend configuration.
Supports both SQLAlchemy (PostgreSQL) and Beanie (MongoDB) backends dynamically.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.security import setup_security_headers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Unified backend detection using environment variable
BACKEND_TYPE = os.getenv("BACKEND_TYPE", "sqlalchemy")

# Import unified database configuration
from app.db.database import (
    BACKEND_TYPE,
    None,
    "beanie",
    "sqlalchemy",
    ==,
    else,
    engine,
    if,
    init_database,
)

# Import FastAPI-Users configuration based on backend
if BACKEND_TYPE == "sqlalchemy":
    from app.auth.manager import auth_backend, current_active_user, fastapi_users
    from app.auth.models import User
    from app.db.base import Base
else:
    from app.auth.manager_beanie import auth_backend, current_active_user, fastapi_users
    from app.auth.models_beanie import User


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application lifespan events.
    
    This function handles startup and shutdown events for the FastAPI app,
    including database initialization based on the selected backend.
    """
    # Startup
    print("🚀 Starting up...")
    print(f"📋 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug mode: {settings.DEBUG}")
    print(f"🗄️ Backend: {BACKEND_TYPE}")
    
    if BACKEND_TYPE == "sqlalchemy":
        # Create database tables for SQLAlchemy
        if settings.ENVIRONMENT == "development":
            print("🗄️ Creating database tables...")
            Base.metadata.create_all(bind=engine)
    elif BACKEND_TYPE == "beanie":
        # Initialize MongoDB for Beanie
        print("🗄️ Initializing MongoDB connection...")
        await init_database()
    else:
        raise ValueError(f"Unsupported backend type: {BACKEND_TYPE}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    # Add cleanup tasks here if needed


# Create FastAPI instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT == "development" else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.ALLOWED_HOSTS:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# Setup security headers
setup_security_headers(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include FastAPI-Users routers
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_verify_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(),
    prefix="/users",
    tags=["users"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to FastAPI Full-stack Template",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": f"{settings.API_V1_STR}/docs",
        "health": f"{settings.API_V1_STR}/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }