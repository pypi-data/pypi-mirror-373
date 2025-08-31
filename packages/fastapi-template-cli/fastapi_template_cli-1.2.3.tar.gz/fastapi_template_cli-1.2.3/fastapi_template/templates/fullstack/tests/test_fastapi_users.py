"""
Tests for FastAPI-Users integration.
"""

import pytest
from app.db.database import async_session_maker
from app.main import app
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def async_client() -> AsyncClient:
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db_session() -> AsyncSession:
    """Create a database session for testing."""
    async with async_session_maker() as session:
        yield session


@pytest.mark.asyncio
async def test_user_registration(async_client: AsyncClient):
    """Test user registration endpoint."""
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "username": "testuser",
            "full_name": "Test User",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_user_login(async_client: AsyncClient):
    """Test user login endpoint."""
    # First register a user
    await async_client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "loginpassword123",
            "username": "loginuser",
            "full_name": "Login User",
        },
    )

    # Then login
    response = await async_client.post(
        "/auth/jwt/login",
        data={"username": "login@example.com", "password": "loginpassword123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_current_user(async_client: AsyncClient):
    """Test getting current user profile."""
    # Register and login
    await async_client.post(
        "/auth/register",
        json={
            "email": "profile@example.com",
            "password": "profilepassword123",
            "username": "profileuser",
            "full_name": "Profile User",
        },
    )

    login_response = await async_client.post(
        "/auth/jwt/login",
        data={"username": "profile@example.com", "password": "profilepassword123"},
    )

    token = login_response.json()["access_token"]

    # Get current user
    response = await async_client.get(
        "/users/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profile@example.com"
    assert data["username"] == "profileuser"


@pytest.mark.asyncio
async def test_update_user_profile(async_client: AsyncClient):
    """Test updating user profile."""
    # Register and login
    await async_client.post(
        "/auth/register",
        json={
            "email": "update@example.com",
            "password": "updatepassword123",
            "username": "updateuser",
            "full_name": "Update User",
        },
    )

    login_response = await async_client.post(
        "/auth/jwt/login",
        data={"username": "update@example.com", "password": "updatepassword123"},
    )

    token = login_response.json()["access_token"]

    # Update profile
    response = await async_client.patch(
        "/users/me",
        json={"full_name": "Updated Name"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_password_reset_flow(async_client: AsyncClient):
    """Test password reset flow."""
    # Register user
    await async_client.post(
        "/auth/register",
        json={
            "email": "reset@example.com",
            "password": "oldpassword123",
            "username": "resetuser",
            "full_name": "Reset User",
        },
    )

    # Request password reset
    response = await async_client.post(
        "/auth/forgot-password", json={"email": "reset@example.com"}
    )

    assert response.status_code == 202


@pytest.mark.asyncio
async def test_registration_validation(async_client: AsyncClient):
    """Test registration validation."""
    # Test duplicate email
    await async_client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "username": "user1",
            "full_name": "User One",
        },
    )

    response = await async_client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "username": "user2",
            "full_name": "User Two",
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_protected_endpoint_without_auth(async_client: AsyncClient):
    """Test accessing protected endpoint without authentication."""
    response = await async_client.get("/users/me")
    assert response.status_code == 401
