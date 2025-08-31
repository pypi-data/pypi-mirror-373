"""
Tests for main application.
"""

from app.core.config import settings
from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI Fullstack API"}


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_v1_health(client: TestClient) -> None:
    """Test API v1 health check."""
    response = client.get(f"{settings.API_V1_STR}/health/")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok"
