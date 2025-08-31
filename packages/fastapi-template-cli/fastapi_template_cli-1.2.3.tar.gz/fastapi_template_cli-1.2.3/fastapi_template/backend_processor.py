"""Backend processor for dynamic template generation with modular authentication."""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

from .auth_template_generator import AuthTemplateGenerator


class BackendProcessor:
    """Handles all conditional processing and logic evaluation during template generation."""

    def __init__(self, template_path: Path, target_path: Path):
        self.template_path = template_path
        self.target_path = target_path
        self.config = {}
        self.processed_files = []

    def process_template(self, user_config: Dict[str, Any]) -> None:
        """Process all user selections and generate static templates."""
        self.config = user_config

        # Process all conditional logic upfront
        self._validate_config()
        self._process_requirements()
        self._process_database_content()
        self._process_environment_files()
        self._process_docker_files()
        self._process_application_files()

        # Generate static templates
        self._copy_static_files()
        self._generate_static_config()

    def _validate_config(self) -> None:
        """Validate user configuration and set defaults."""
        template_type = self.config.get("template_type", "minimal")
        backend = self.config.get("backend", "sqlalchemy")

        self.config.update(
            {
                "template_type": template_type,
                "backend": backend,
                "include_auth": template_type == "fullstack",
                "include_database": template_type in ["api_only", "fullstack"],
                "include_docker": template_type in ["api_only", "fullstack"],
                "include_tests": template_type in ["api_only", "fullstack"],
            }
        )

    def _process_requirements(self) -> None:
        """Generate requirements.txt with exact dependencies based on user choices."""
        requirements = self._get_base_requirements()

        if self.config["template_type"] == "minimal":
            requirements.extend(["fastapi>=0.104.0", "uvicorn[standard]>=0.23.0"])
        elif self.config["template_type"] == "api_only":
            requirements.extend(
                [
                    "fastapi>=0.104.0",
                    "uvicorn[standard]>=0.23.0",
                    "sqlalchemy>=2.0.0",
                    "alembic>=1.12.0",
                    "psycopg2-binary>=2.9.0",
                    "python-dotenv>=1.0.0",
                ]
            )
        elif self.config["template_type"] == "fullstack":
            if self.config["backend"] == "sqlalchemy":
                requirements.extend(
                    [
                        "fastapi>=0.104.0",
                        "uvicorn[standard]>=0.23.0",
                        "sqlalchemy>=2.0.0",
                        "alembic>=1.12.0",
                        "psycopg2-binary>=2.9.0",
                        "python-dotenv>=1.0.0",
                        "fastapi-users[sqlalchemy]>=12.0.0",
                        "passlib[bcrypt]>=1.7.4",
                        "python-jose[cryptography]>=3.3.0",
                        "python-multipart>=0.0.6",
                    ]
                )
            else:  # beanie
                requirements.extend(
                    [
                        "fastapi>=0.104.0",
                        "uvicorn[standard]>=0.23.0",
                        "motor>=3.3.0",
                        "beanie>=1.23.0",
                        "python-dotenv>=1.0.0",
                        "fastapi-users[beanie]>=12.0.0",
                        "passlib[bcrypt]>=1.7.4",
                        "python-jose[cryptography]>=3.3.0",
                        "python-multipart>=0.0.6",
                    ]
                )

        # Ensure target directory exists
        self.target_path.mkdir(parents=True, exist_ok=True)

        # Write final requirements file
        requirements_path = self.target_path / "requirements.txt"
        with open(requirements_path, "w") as f:
            f.write("\n".join(requirements))

    def _get_base_requirements(self) -> List[str]:
        """Get base requirements common to all templates."""
        return ["# Base dependencies", "pydantic>=2.0.0", "pydantic-settings>=2.0.0"]

    def _process_database_content(self) -> None:
        """Generate database-specific content based on user choices."""
        if not self.config["include_database"]:
            return

        if self.config["backend"] == "sqlalchemy":
            self._generate_sqlalchemy_content()
        else:
            self._generate_beanie_content()

    def _generate_sqlalchemy_content(self) -> None:
        """Generate SQLAlchemy-specific database content."""
        # Create alembic directory structure
        alembic_dir = self.target_path / "alembic"
        alembic_dir.mkdir(exist_ok=True)

        # Generate alembic.ini
        alembic_ini_content = self._get_sqlalchemy_alembic_ini()
        with open(self.target_path / "alembic.ini", "w") as f:
            f.write(alembic_ini_content)

        # Generate alembic env.py
        env_py_content = self._get_sqlalchemy_env_py()
        with open(alembic_dir / "env.py", "w") as f:
            f.write(env_py_content)

        # Generate versions directory
        (alembic_dir / "versions").mkdir(exist_ok=True)

    def _generate_beanie_content(self) -> None:
        """Generate Beanie-specific database content."""
        # Remove SQLAlchemy-specific files for Beanie
        files_to_remove = ["alembic.ini", "alembic"]

        for file_name in files_to_remove:
            path = self.target_path / file_name
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()

    def _process_environment_files(self) -> None:
        """Generate environment files with backend-specific configurations."""
        # Generate .env.example
        env_example_content = self._get_env_example_content()
        with open(self.target_path / ".env.example", "w") as f:
            f.write(env_example_content)

        # Generate .env with selected backend
        env_content = self._get_env_content()
        with open(self.target_path / ".env", "w") as f:
            f.write(env_content)

    def _process_docker_files(self) -> None:
        """Generate Docker configuration based on user choices."""
        if not self.config["include_docker"]:
            return

        # Always create docker-compose.yml with appropriate backend configuration
        docker_content = self._get_docker_compose_content()
        with open(self.target_path / "docker-compose.yml", "w") as f:
            f.write(docker_content)

        # Remove backend-specific docker files
        if self.config["backend"] == "sqlalchemy":
            mongo_compose = self.target_path / "docker-compose.mongo.yml"
            if mongo_compose.exists():
                mongo_compose.unlink()
        else:  # beanie
            mongo_compose = self.target_path / "docker-compose.mongo.yml"
            if mongo_compose.exists():
                mongo_compose.unlink()

    def _process_application_files(self) -> None:
        """Generate application files with pre-processed content."""
        # Ensure app directory structure exists
        app_dir = self.target_path / "app"
        db_dir = app_dir / "db"
        models_dir = app_dir / "models"
        schemas_dir = app_dir / "schemas"
        crud_dir = app_dir / "crud"
        api_dir = app_dir / "api"
        auth_dir = app_dir / "auth"

        db_dir.mkdir(parents=True, exist_ok=True)
        models_dir.mkdir(parents=True, exist_ok=True)
        schemas_dir.mkdir(parents=True, exist_ok=True)
        crud_dir.mkdir(parents=True, exist_ok=True)
        api_dir.mkdir(parents=True, exist_ok=True)
        auth_dir.mkdir(parents=True, exist_ok=True)

        # Generate database.py with static backend configuration
        database_content = self._get_database_content()
        with open(db_dir / "database.py", "w") as f:
            f.write(database_content)

        # Generate schemas
        self._generate_schemas_content()

        # Generate CRUD operations
        self._generate_crud_content()

        # Generate API routers
        self._generate_api_content()

        # Generate main.py with static backend configuration
        main_content = self._get_main_content()
        with open(app_dir / "main.py", "w") as f:
            f.write(main_content)

        # Process auth files based on backend selection
        self._process_auth_files(auth_dir)

    def _process_auth_files(self, auth_dir: Path) -> None:
        """Process authentication files using dynamic backend-specific generation."""
        if not self.config["include_auth"]:
            # Remove auth directory if auth is not included
            if auth_dir.exists():
                shutil.rmtree(auth_dir)
            return

        auth_dir.mkdir(parents=True, exist_ok=True)

        # Use dynamic template generator
        generator = AuthTemplateGenerator(self.config["backend"])

        # Generate backend-specific files
        models_content = generator.generate_models_file()
        manager_content = generator.generate_manager_file()
        config_content = generator.generate_config_file()

        # Write generated files
        with open(auth_dir / "models.py", "w") as f:
            f.write(models_content)

        with open(auth_dir / "manager.py", "w") as f:
            f.write(manager_content)

        with open(auth_dir / "config.py", "w") as f:
            f.write(config_content)

        # Create __init__.py
        init_content = '"""Authentication package for FastAPI-Users integration."""\n'
        with open(auth_dir / "__init__.py", "w") as f:
            f.write(init_content)

    def _copy_static_files(self) -> None:
        """Copy static files that don't need processing."""
        # Copy all files from template, then process conditional ones
        # The copy happens in CLI, so this is handled by shutil.copytree

    def _generate_static_config(self) -> None:
        """Generate static configuration file."""
        config = {
            "template_type": self.config["template_type"],
            "backend": self.config["backend"],
            "include_auth": self.config["include_auth"],
            "include_database": self.config["include_database"],
            "include_docker": self.config["include_docker"],
            "include_tests": self.config["include_tests"],
        }

        config_path = self.target_path / ".template_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

    # Content generation methods
    def _get_sqlalchemy_alembic_ini(self) -> str:
        """Generate SQLAlchemy-specific alembic.ini content."""
        return """# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration file names
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d%%(second).2d_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
timezone = UTC

# max length of characters to apply to the
# "slug" field
truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
sourceless = false

# version location specification
version_locations = %(here)s/bar

# the output encoding used when revision files
# are written from script.py.mako
output_encoding = utf-8

sqlalchemy.url = postgresql://user:password@localhost/fastapi_db

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

    def _get_sqlalchemy_env_py(self) -> str:
        """Generate SQLAlchemy-specific alembic env.py content."""
        return '''"""Alembic environment configuration."""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.db.database import Base
from app.models import user, item  # noqa: F401

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

    def _get_env_example_content(self) -> str:
        """Generate environment file content based on configuration."""
        content = ["# Environment Configuration"]

        if self.config["include_database"]:
            if self.config["backend"] == "sqlalchemy":
                content.extend(
                    [
                        "",
                        "# Database Configuration (PostgreSQL)",
                        "DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_db",
                        "",
                        "# For SQLite during development",
                        "# DATABASE_URL=sqlite:///./app.db",
                    ]
                )
            else:
                content.extend(
                    [
                        "",
                        "# Database Configuration (MongoDB)",
                        "MONGODB_URL=mongodb://localhost:27017/fastapi_db",
                        "DATABASE_NAME=fastapi_db",
                    ]
                )

        if self.config["include_auth"]:
            content.extend(
                [
                    "",
                    "# Security Configuration",
                    "SECRET_KEY=your-secret-key-here-change-this-in-production",
                    "ALGORITHM=HS256",
                    "ACCESS_TOKEN_EXPIRE_MINUTES=30",
                ]
            )

        content.extend(
            ["", "# Backend Configuration", f"BACKEND_TYPE={self.config['backend']}"]
        )

        return "\n".join(content)

    def _get_env_content(self) -> str:
        """Generate .env file content with selected backend."""
        return self._get_env_example_content().replace(
            "your-secret-key-here-change-this-in-production",
            "dev-secret-key-change-in-production",
        )

    def _get_database_content(self) -> str:
        """Generate static database.py content based on backend."""
        if self.config["backend"] == "sqlalchemy":
            return '''"""Database configuration for SQLAlchemy backend."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Database dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)
'''
        else:
            return '''"""Database configuration for Beanie backend."""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from dotenv import load_dotenv
from app.models.user import User
from app.models.item import Item

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/fastapi_db")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fastapi_db")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]


async def init_database():
    """Initialize Beanie with document models."""
    await init_beanie(
        database=database,
        document_models=[User, Item]
    )


def get_db():
    """Database dependency for FastAPI (async)."""
    return database


async def drop_database():
    """Drop the entire database."""
    await client.drop_database(DATABASE_NAME)
'''

    def _generate_models_content(self) -> None:
        """Generate static models based on backend configuration."""
        # Generate User model
        if self.config["include_auth"]:
            user_content = self._get_user_model_content()
        else:
            user_content = self._get_basic_user_model_content()

        with open(self.target_path / "app" / "models" / "user.py", "w") as f:
            f.write(user_content)

        # Generate Item model
        item_content = self._get_item_model_content()
        with open(self.target_path / "app" / "models" / "item.py", "w") as f:
            f.write(item_content)

    def _get_user_model_content(self) -> str:
        """Generate User model based on backend and auth requirements."""
        if self.config["backend"] == "sqlalchemy":
            return '''"""User model for SQLAlchemy backend."""

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    """User model with SQLAlchemy ORM."""
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to items
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
'''
        else:
            return '''"""User model for Beanie backend."""

from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class User(Document):
    """User model with Beanie ODM."""
    
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "users"
        indexes = [
            [("email", 1)],
            [("username", 1)]
        ]
'''

    def _get_basic_user_model_content(self) -> str:
        """Generate basic User model without auth."""
        if self.config["backend"] == "sqlalchemy":
            return '''"""Basic User model for SQLAlchemy backend."""

from sqlalchemy import Column, Integer, String
from app.db.database import Base


class User(Base):
    """Basic User model without authentication."""
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
'''
        else:
            return '''"""Basic User model for Beanie backend."""

from beanie import Document
from pydantic import Field


class User(Document):
    """Basic User model without authentication."""
    
    name: str
    email: str = Field(unique=True, index=True)

    class Settings:
        name = "users"
'''

    def _get_item_model_content(self) -> str:
        """Generate Item model based on backend."""
        if self.config["backend"] == "sqlalchemy":
            return '''"""Item model for SQLAlchemy backend."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Item(Base):
    """Item model with SQLAlchemy ORM."""
    
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    price = Column(Numeric(10, 2))
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="items")
'''
        else:
            return '''"""Item model for Beanie backend."""

from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class Item(Document):
    """Item model with Beanie ODM."""
    
    title: str = Field(index=True)
    description: Optional[str] = None
    price: float
    owner_id: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "items"
'''

    def _get_docker_compose_content(self) -> str:
        """Generate Docker Compose content based on backend."""
        if self.config["backend"] == "sqlalchemy":
            return """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/fastapi_db
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=fastapi_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:"""
        else:  # beanie
            return """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017/fastapi_db
    depends_on:
      - mongo

  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:"""

    def _get_main_content(self) -> str:
        """Generate main.py content based on configuration."""
        imports = ["from fastapi import FastAPI"]
        app_content = []

        if self.config["include_database"]:
            if self.config["backend"] == "sqlalchemy":
                imports.extend(
                    [
                        "from contextlib import asynccontextmanager",
                        "from sqlalchemy import text",
                        "from app.db.database import engine, Base",
                        "from app.db.database import SessionLocal",
                    ]
                )
                app_content.extend(
                    [
                        "",
                        "@asynccontextmanager",
                        "async def lifespan(app: FastAPI):",
                        "    # Create database tables",
                        "    Base.metadata.create_all(bind=engine)",
                        "    yield",
                        "",
                        "app = FastAPI(lifespan=lifespan)",
                    ]
                )
            else:  # beanie
                imports.extend(
                    [
                        "from contextlib import asynccontextmanager",
                        "from app.db.database import init_database",
                    ]
                )
                app_content.extend(
                    [
                        "",
                        "@asynccontextmanager",
                        "async def lifespan(app: FastAPI):",
                        "    # Initialize database",
                        "    await init_database()",
                        "    yield",
                        "",
                        "app = FastAPI(lifespan=lifespan)",
                    ]
                )
        else:
            app_content = ["", "app = FastAPI()"]

        # Add routes
        routes = [
            "",
            '@app.get("/")',
            "async def root():",
            '    return {"message": "Hello World"}',
            "",
            '@app.get("/health")',
            "async def health_check():",
            '    return {"status": "healthy"}',
        ]

        # Add database-dependent routes if database is included
        if self.config["include_database"]:
            if self.config["backend"] == "sqlalchemy":
                routes.extend(
                    [
                        "",
                        "from sqlalchemy.orm import Session",
                        "from app.db.database import get_db",
                        "from app.models.user import User",
                        "from app.models.item import Item",
                        "from app.schemas.user import UserCreate, UserResponse",
                        "from app.schemas.item import ItemCreate, ItemResponse",
                        "",
                        "@app.get('/users', response_model=list[UserResponse])",
                        "async def get_users(db: Session = get_db()):",
                        "    users = db.query(User).all()",
                        "    return users",
                        "",
                        "@app.post('/users', response_model=UserResponse)",
                        "async def create_user(user: UserCreate, db: Session = get_db()):",
                        "    from app.crud.user import create_user as crud_create_user",
                        "    return crud_create_user(db=db, user=user)",
                        "",
                        "@app.get('/items', response_model=list[ItemResponse])",
                        "async def get_items(db: Session = get_db()):",
                        "    items = db.query(Item).all()",
                        "    return items",
                        "",
                        "@app.post('/items', response_model=ItemResponse)",
                        "async def create_item(item: ItemCreate, db: Session = get_db()):",
                        "    from app.crud.item import create_item as crud_create_item",
                        "    return crud_create_item(db=db, item=item)",
                    ]
                )
            else:  # beanie
                routes.extend(
                    [
                        "",
                        "from beanie import PydanticObjectId",
                        "from app.models.user import User",
                        "from app.models.item import Item",
                        "from app.schemas.user import UserCreate, UserResponse",
                        "from app.schemas.item import ItemCreate, ItemResponse",
                        "",
                        "@app.get('/users', response_model=list[UserResponse])",
                        "async def get_users():",
                        "    users = await User.find_all().to_list()",
                        "    return users",
                        "",
                        "@app.post('/users', response_model=UserResponse)",
                        "async def create_user(user: UserCreate):",
                        "    from app.crud.user import create_user as crud_create_user",
                        "    return await crud_create_user(user=user)",
                        "",
                        "@app.get('/items', response_model=list[ItemResponse])",
                        "async def get_items():",
                        "    items = await Item.find_all().to_list()",
                        "    return items",
                        "",
                        "@app.post('/items', response_model=ItemResponse)",
                        "async def create_item(item: ItemCreate):",
                        "    from app.crud.item import create_item as crud_create_item",
                        "    return await crud_create_item(item=item)",
                    ]
                )

        # Add authentication routes if auth is included
        if self.config["include_auth"]:
            routes.extend(
                [
                    "",
                    "# Include authentication routes",
                    "from app.api.api_v1.api import api_router",
                    'app.include_router(api_router, prefix="/api/v1")',
                ]
            )

        return "\n".join(imports + app_content + routes)
