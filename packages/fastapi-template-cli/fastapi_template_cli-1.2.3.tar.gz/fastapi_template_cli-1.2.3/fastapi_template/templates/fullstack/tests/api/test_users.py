"""
Tests for user endpoints.
"""

from app.core.config import settings
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.utils.user import create_test_user


def test_get_users_superuser_me(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test get current superuser."""
    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    current_user = response.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is True
    assert current_user["email"] == settings.FIRST_SUPERUSER


def test_get_users_normal_user_me(client: TestClient, session: Session) -> None:
    """Test get current normal user."""
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
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=headers,
    )
    assert response.status_code == 200
    current_user = response.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["email"] == user.email


def test_create_user_new_email(
    client: TestClient, superuser_token_headers: dict[str, str], session: Session
) -> None:
    """Test create user with new email."""
    username = "newuser"
    password = "testpassword"
    data = {
        "email": "newuser@example.com",
        "username": username,
        "password": password,
        "full_name": "New User",
    }
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == data["email"]
    assert user["username"] == data["username"]
    assert "hashed_password" not in user


def test_get_existing_user(
    client: TestClient, superuser_token_headers: dict[str, str], session: Session
) -> None:
    """Test get existing user."""
    user = create_test_user(session)
    response = client.get(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    api_user = response.json()
    assert user.email == api_user["email"]


def test_create_user_existing_username(
    client: TestClient, superuser_token_headers: dict[str, str], session: Session
) -> None:
    """Test create user with existing username."""
    user = create_test_user(session)
    data = {
        "email": "newemail@example.com",
        "username": user.username,
        "password": "testpassword",
        "full_name": "New User",
    }
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_create_user_by_normal_user(client: TestClient, session: Session) -> None:
    """Test create user by normal user (should fail)."""
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
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "testpassword",
        "full_name": "New User",
    }
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=headers,
        json=data,
    )
    assert response.status_code == 403
