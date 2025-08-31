"""
Main FastAPI application for API Only template.
This demonstrates a clean, modular FastAPI structure.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.config import settings
from app.routers import health, items
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application lifespan events.

    This function handles startup and shutdown events for the FastAPI app.
    """
    # Startup
    print("🚀 Starting up...")
    print(f"📋 Environment: {settings.ENVIRONMENT}")

    yield

    # Shutdown
    print("🛑 Shutting down...")


# Create FastAPI instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to FastAPI API Only Template",
        "version": settings.VERSION,
        "docs": "/docs",
    }
