"""
Tests for the items router.
"""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_create_item():
    """Test creating a new item."""
    item_data = {
        "name": "Test Item",
        "description": "A test item",
        "price": 29.99,
        "is_available": True,
    }

    response = client.post("/api/v1/items/", json=item_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]
    assert data["price"] == item_data["price"]
    assert data["is_available"] == item_data["is_available"]
    assert "id" in data


def test_list_items():
    """Test listing items."""
    # Create a test item first
    item_data = {"name": "Test Item", "price": 19.99, "is_available": True}
    client.post("/api/v1/items/", json=item_data)

    response = client.get("/api/v1/items/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_item():
    """Test getting a specific item."""
    # Create a test item
    item_data = {"name": "Specific Item", "price": 39.99, "is_available": True}
    create_response = client.post("/api/v1/items/", json=item_data)
    item_id = create_response.json()["id"]

    response = client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == item_data["name"]


def test_get_nonexistent_item():
    """Test getting a non-existent item."""
    fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/api/v1/items/{fake_uuid}")
    assert response.status_code == 404


def test_update_item():
    """Test updating an existing item."""
    # Create a test item
    item_data = {"name": "Original Item", "price": 49.99, "is_available": True}
    create_response = client.post("/api/v1/items/", json=item_data)
    item_id = create_response.json()["id"]

    # Update the item
    update_data = {"name": "Updated Item", "price": 59.99}
    response = client.put(f"/api/v1/items/{item_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated Item"
    assert data["price"] == 59.99


def test_delete_item():
    """Test deleting an item."""
    # Create a test item
    item_data = {"name": "To Delete", "price": 9.99, "is_available": True}
    create_response = client.post("/api/v1/items/", json=item_data)
    item_id = create_response.json()["id"]

    # Delete the item
    response = client.delete(f"/api/v1/items/{item_id}")
    assert response.status_code == 200

    # Verify it's deleted
    get_response = client.get(f"/api/v1/items/{item_id}")
    assert get_response.status_code == 404
