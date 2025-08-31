"""
User test utilities and factories.
"""

from app.core.security import get_password_hash
from app.models.user import User
from factory import Factory, Faker, LazyAttribute, Sequence
from sqlalchemy.orm import Session


class UserFactory(Factory):
    """User factory for testing."""

    class Meta:
        model = User

    email = Sequence(lambda n: f"user{n}@example.com")
    username = Sequence(lambda n: f"user{n}")
    full_name = Faker("name")
    hashed_password = LazyAttribute(lambda obj: get_password_hash("testpassword"))
    is_active = True
    is_superuser = False


class SuperUserFactory(UserFactory):
    """Superuser factory for testing."""

    email = "admin@example.com"
    username = "admin"
    full_name = "Admin User"
    is_superuser = True


def create_test_user(
    db: Session,
    email: str = "test@example.com",
    password: str = "testpassword",
    is_superuser: bool = False,
) -> User:
    """Create a test user."""
    user = UserFactory(
        email=email,
        hashed_password=get_password_hash(password),
        is_superuser=is_superuser,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
