"""
Health check endpoints.
"""

from datetime import datetime
from typing import Any, Dict

from app.db.database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive health check including database connectivity.

    Args:
        db: Database session

    Returns:
        Health status information
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "fastapi-fullstack",
        "version": "1.0.0",
        "database": "connected",
    }

    # Check database connectivity
    try:
        db.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = "disconnected"
        health_status["database_error"] = str(e)
        health_status["status"] = "unhealthy"

    return health_status


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed health check with system information.

    Args:
        db: Database session

    Returns:
        Detailed health information
    """
    import os
    import sys

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "fastapi-fullstack",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "unknown"),
        "python_version": sys.version,
        "database": "connected",
        "system": {
            "pid": os.getpid(),
            "cwd": os.getcwd(),
            "platform": sys.platform,
        },
    }

    # Check database connectivity
    try:
        db.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = "disconnected"
        health_status["database_error"] = str(e)
        health_status["status"] = "unhealthy"

    return health_status
