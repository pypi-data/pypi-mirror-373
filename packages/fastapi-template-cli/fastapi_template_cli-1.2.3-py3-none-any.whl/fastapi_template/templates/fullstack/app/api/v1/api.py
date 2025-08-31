"""
Main API router for version 1.
"""

from app.api.v1.endpoints import health, items
from fastapi import APIRouter

api_router = APIRouter()

# Include core endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
