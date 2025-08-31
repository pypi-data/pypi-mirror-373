"""
Example items router demonstrating modular endpoints.
"""

from typing import List, Optional
from uuid import UUID, uuid4

from app.models.items import Item, ItemCreate, ItemUpdate
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

# In-memory storage for demo purposes
items_db: dict[str, Item] = {}


@router.post("/", response_model=Item)
async def create_item(item: ItemCreate) -> Item:
    """
    Create a new item.

    Args:
        item: Item creation data

    Returns:
        The created item
    """
    new_item = Item(
        id=uuid4(),
        name=item.name,
        description=item.description,
        price=item.price,
        is_available=item.is_available,
    )
    items_db[str(new_item.id)] = new_item
    return new_item


@router.get("/", response_model=List[Item])
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_available: Optional[bool] = None,
) -> List[Item]:
    """
    List items with optional filtering and pagination.

    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        is_available: Filter by availability

    Returns:
        List of items
    """
    items = list(items_db.values())

    if is_available is not None:
        items = [item for item in items if item.is_available == is_available]

    return items[skip : skip + limit]


@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: UUID) -> Item:
    """
    Get a specific item by ID.

    Args:
        item_id: UUID of the item

    Returns:
        The requested item

    Raises:
        HTTPException: If item not found
    """
    item = items_db.get(str(item_id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: UUID, item_update: ItemUpdate) -> Item:
    """
    Update an existing item.

    Args:
        item_id: UUID of the item
        item_update: Update data

    Returns:
        The updated item

    Raises:
        HTTPException: If item not found
    """
    item = items_db.get(str(item_id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    items_db[str(item_id)] = item
    return item


@router.delete("/{item_id}")
async def delete_item(item_id: UUID) -> dict[str, str]:
    """
    Delete an item.

    Args:
        item_id: UUID of the item

    Returns:
        Success message

    Raises:
        HTTPException: If item not found
    """
    if str(item_id) not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    del items_db[str(item_id)]
    return {"message": "Item deleted successfully"}
