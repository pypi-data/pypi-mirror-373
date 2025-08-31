"""
Health check endpoints.
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.

    Returns:
        Dict containing health status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "fastapi-api-only",
    }


@router.get("/detailed")
async def detailed_health() -> Dict[str, Any]:
    """
    Detailed health check with system information.

    Returns:
        Dict containing detailed health information
    """
    import os
    import sys

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "fastapi-api-only",
        "version": "1.0.0",
        "python_version": sys.version,
        "environment": {
            "pid": os.getpid(),
            "cwd": os.getcwd(),
        },
    }
