"""
Tests for authentication endpoints.
"""

from app.core.config import settings
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.utils.user import create_test_user


def test_register_user(client: TestClient, session: Session) -> None:
    """Test user registration."""
    data = {
        "email": "newuser@example.com",
        "password": "testpassword",
        "full_name": "New User",
        "username": "newuser",
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=data,
    )
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == data["email"]
    assert "hashed_password" not in user


def test_register_user_existing_email(client: TestClient, session: Session) -> None:
    """Test registration with existing email."""
    create_test_user(session, email="existing@example.com")
    data = {
        "email": "existing@example.com",
        "password": "testpassword",
        "full_name": "Existing User",
        "username": "existing",
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=data,
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_access_token(client: TestClient, session: Session) -> None:
    """Test login access token."""
    user = create_test_user(session)
    login_data = {
        "username": user.email,
        "password": "testpassword",
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
    )
    tokens = response.json()
    assert response.status_code == 200
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_incorrect_password(client: TestClient, session: Session) -> None:
    """Test login with incorrect password."""
    user = create_test_user(session)
    login_data = {
        "username": user.email,
        "password": "wrongpassword",
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
    )
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_inactive_user(client: TestClient, session: Session) -> None:
    """Test login with inactive user."""
    user = create_test_user(session)
    user.is_active = False
    session.add(user)
    session.commit()

    login_data = {
        "username": user.email,
        "password": "testpassword",
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
    )
    assert response.status_code == 400
    assert "Inactive user" in response.json()["detail"]
