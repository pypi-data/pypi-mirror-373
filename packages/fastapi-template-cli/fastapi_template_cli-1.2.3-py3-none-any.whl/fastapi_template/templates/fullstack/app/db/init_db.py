"""
Database initialization script.
"""

from app.core.config import settings
from app.crud.user import user as crud_user
from app.db.database import SessionLocal
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session


def init_db(db: Session) -> None:
    """Initialize the database with default data."""
    # Create superuser if it doesn't exist
    user = crud_user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Admin User",
            username="admin",
        )
        user = crud_user.create(db, obj_in=user_in)
        user.is_superuser = True
        db.add(user)
        db.commit()
        db.refresh(user)


def main() -> None:
    """Main function to initialize database."""
    db = SessionLocal()
    init_db(db)
    db.close()
    print("Database initialized successfully!")


if __name__ == "__main__":
    main()
