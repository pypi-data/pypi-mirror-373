"""
Tests for the main FastAPI application.
"""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Welcome to FastAPI API Only Template" in data["message"]
    assert "version" in data
    assert "docs" in data


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "fastapi-api-only"


def test_detailed_health():
    """Test the detailed health endpoint."""
    response = client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "python_version" in data
    assert "environment" in data
