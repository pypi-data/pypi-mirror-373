#!/usr/bin/env python3
"""
Setup script for FastAPI-Users integration.

This script helps with:
1. Setting up the database based on selected backend
2. Creating initial superuser
3. Running migrations for SQLAlchemy
4. Initializing MongoDB for Beanie
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.auth.models import User as SQLAlchemyUser
from app.auth.models_beanie import User as BeanieUser
from app.core.config import settings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


class FastAPIUsersSetup:
    def __init__(self):
        self.backend = os.getenv("FASTAPI_USERS_BACKEND", "sqlalchemy")
        print(f"Setting up FastAPI-Users with backend: {self.backend}")

    async def setup_sqlalchemy(self):
        """Setup SQLAlchemy backend."""
        print("Setting up SQLAlchemy backend...")

        # Run migrations
        print("Running database migrations...")
        os.system("alembic upgrade head")

        # Create superuser if it doesn't exist
        await self.create_sqlalchemy_superuser()

        print("SQLAlchemy backend setup complete!")

    async def create_sqlalchemy_superuser(self):
        """Create superuser for SQLAlchemy backend."""
        try:
            engine = create_async_engine(settings.DATABASE_URL)
            async_session = sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )

            async with async_session() as session:
                # Check if superuser already exists
                result = await session.execute(
                    text("SELECT * FROM users WHERE email = :email"),
                    {"email": settings.FIRST_SUPERUSER},
                )

                if result.first():
                    print(f"Superuser {settings.FIRST_SUPERUSER} already exists")
                    return

                # Create superuser
                from fastapi_users.password import PasswordHelper

                password_helper = PasswordHelper()
                hashed_password = password_helper.hash(
                    settings.FIRST_SUPERUSER_PASSWORD
                )

                superuser = SQLAlchemyUser(
                    email=settings.FIRST_SUPERUSER,
                    hashed_password=hashed_password,
                    username="admin",
                    full_name="Administrator",
                    is_active=True,
                    is_superuser=True,
                    is_verified=True,
                )

                session.add(superuser)
                await session.commit()

                print(f"Superuser {settings.FIRST_SUPERUSER} created successfully")

        except Exception as e:
            print(f"Error creating superuser: {e}")

    async def setup_beanie(self):
        """Setup Beanie/MongoDB backend."""
        print("Setting up Beanie/MongoDB backend...")

        try:
            from beanie import init_beanie
            from motor.motor_asyncio import AsyncIOMotorClient

            # Initialize MongoDB connection
            client = AsyncIOMotorClient(settings.MONGODB_URL)
            await init_beanie(
                database=client[settings.DATABASE_NAME], document_models=[BeanieUser]
            )

            # Create superuser if it doesn't exist
            await self.create_beanie_superuser()

            print("Beanie backend setup complete!")

        except Exception as e:
            print(f"Error setting up Beanie backend: {e}")

    async def create_beanie_superuser(self):
        """Create superuser for Beanie backend."""
        try:
            # Check if superuser already exists
            existing_user = await BeanieUser.find_one(
                BeanieUser.email == settings.FIRST_SUPERUSER
            )

            if existing_user:
                print(f"Superuser {settings.FIRST_SUPERUSER} already exists")
                return

            # Create superuser
            from fastapi_users.password import PasswordHelper

            password_helper = PasswordHelper()
            hashed_password = password_helper.hash(settings.FIRST_SUPERUSER_PASSWORD)

            superuser = BeanieUser(
                email=settings.FIRST_SUPERUSER,
                hashed_password=hashed_password,
                username="admin",
                full_name="Administrator",
                is_active=True,
                is_superuser=True,
                is_verified=True,
            )

            await superuser.create()
            print(f"Superuser {settings.FIRST_SUPERUSER} created successfully")

        except Exception as e:
            print(f"Error creating Beanie superuser: {e}")

    async def run(self):
        """Run the appropriate setup based on backend selection."""
        if self.backend == "sqlalchemy":
            await self.setup_sqlalchemy()
        elif self.backend == "beanie":
            await self.setup_beanie()
        else:
            print(f"Unknown backend: {self.backend}")
            print("Please set FASTAPI_USERS_BACKEND to 'sqlalchemy' or 'beanie'")


async def main():
    """Main setup function."""
    setup = FastAPIUsersSetup()
    await setup.run()


if __name__ == "__main__":
    asyncio.run(main())
