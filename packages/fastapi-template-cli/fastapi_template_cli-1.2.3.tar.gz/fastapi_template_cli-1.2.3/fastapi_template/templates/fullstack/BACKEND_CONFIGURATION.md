# Unified Backend Configuration

This template implements a unified backend configuration system that supports both SQLAlchemy (PostgreSQL) and Beanie (MongoDB) backends within a single, cohesive codebase.

## Overview

The unified configuration system eliminates the need for separate backend-specific files by using:

1. **Environment-based backend detection** via `BACKEND_TYPE` environment variable
2. **Conditional imports and configurations** within unified files
3. **Dynamic model definitions** that adapt to the selected backend
4. **Backend-agnostic API design** that works with both SQLAlchemy and Beanie

## How It Works

### Backend Detection

The system uses the `BACKEND_TYPE` environment variable to determine which backend to use:

- `sqlalchemy` (default): Uses SQLAlchemy ORM with PostgreSQL
- `beanie`: Uses Beanie ODM with MongoDB

### File Structure

Instead of maintaining separate backend-specific files, the unified system uses:

- `app/db/database.py`: Unified database configuration with conditional logic
- `app/models/user.py`: User model with dynamic backend support
- `app/models/item.py`: Item model with dynamic backend support
- `app/main.py`: Unified application initialization

### Configuration Files

The CLI automatically sets up the backend configuration during project creation:

1. **`.env` file**: Contains `BACKEND_TYPE=sqlalchemy|beanie`
2. **`.env.example`**: Includes backend-specific configuration examples
3. **Backend-specific dependencies**: Managed through separate `requirements.txt` files

## Usage

### Creating a New Project

```bash
# SQLAlchemy backend (default)
python -m fastapi_template.cli new myproject --template fullstack

# Beanie backend
python -m fastapi_template.cli new myproject --template fullstack
# Select option 2 for Beanie backend when prompted
```

### Switching Backends

To switch backends in an existing project:

1. Update the `BACKEND_TYPE` in your `.env` file:
   ```bash
   BACKEND_TYPE=beanie  # or sqlalchemy
   ```

2. Update dependencies:
   ```bash
   # For Beanie
   pip install -r requirements_beanie.txt
   
   # For SQLAlchemy
   pip install -r requirements.txt
   ```

3. Restart your application

## Backend-Specific Features

### SQLAlchemy Backend

- **Database**: PostgreSQL with asyncpg driver
- **ORM**: SQLAlchemy with async support
- **Migrations**: Alembic for database schema management
- **Models**: Traditional SQLAlchemy declarative base models

### Beanie Backend

- **Database**: MongoDB with Motor driver
- **ODM**: Beanie for MongoDB document mapping
- **Schema**: Pydantic-based document models
- **Indexing**: MongoDB native indexing support

## Code Examples

### Database Configuration

```python
# app/db/database.py
import os

BACKEND_TYPE = os.getenv("BACKEND_TYPE", "sqlalchemy")

if BACKEND_TYPE == "sqlalchemy":
    # SQLAlchemy configuration
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    # ... SQLAlchemy setup
else:
    # Beanie configuration
    from motor.motor_asyncio import AsyncIOMotorClient
    from beanie import init_beanie
    # ... Beanie setup
```

### Model Definitions

```python
# app/models/user.py
import os

BACKEND_TYPE = os.getenv("BACKEND_TYPE", "sqlalchemy")

if BACKEND_TYPE == "sqlalchemy":
    # SQLAlchemy User model
    class User(Base):
        __tablename__ = "users"
        # ... SQLAlchemy fields
else:
    # Beanie User document
    class User(Document):
        email: str = Field(..., unique=True)
        # ... Beanie fields
```

## Environment Variables

### Common Variables

```bash
# Backend selection
BACKEND_TYPE=sqlalchemy|beanie

# Database configuration
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
MONGODB_DATABASE_URI=mongodb://localhost:27017
MONGODB_DATABASE_NAME=mydatabase
```

### Backend-Specific Variables

#### SQLAlchemy
```bash
SQLALCHEMY_DATABASE_URI=postgresql+asyncpg://user:pass@localhost/dbname
```

#### Beanie
```bash
MONGODB_DATABASE_URI=mongodb://localhost:27017
MONGODB_DATABASE_NAME=mydatabase
```

## Development Workflow

### Adding New Models

When adding new models that need to support both backends:

1. Create the model file with conditional backend logic
2. Define both SQLAlchemy and Beanie versions
3. Use the `BACKEND_TYPE` environment variable for conditional imports
4. Update the database initialization in `app/main.py` if needed

### Testing Both Backends

```bash
# Test SQLAlchemy backend
export BACKEND_TYPE=sqlalchemy
pytest

# Test Beanie backend
export BACKEND_TYPE=beanie
pytest
```

## Benefits

1. **Single Codebase**: No need to maintain separate backend-specific files
2. **Easy Switching**: Change backends with a single environment variable
3. **Clean Architecture**: Unified API design works with both backends
4. **Reduced Complexity**: Fewer files to manage and maintain
5. **Better Testing**: Easier to test both backends in CI/CD
6. **Future-Proof**: Easy to add new backend types in the future

## Migration Guide

### From Separate Backend Files

If you're migrating from separate backend files:

1. **Consolidate models**: Merge backend-specific models into unified files
2. **Update imports**: Use conditional imports based on `BACKEND_TYPE`
3. **Test thoroughly**: Ensure both backends work correctly
4. **Update documentation**: Document the new unified configuration system

### Adding New Backends

To add support for a new backend:

1. Add the new backend type to the `BACKEND_TYPE` detection
2. Create conditional logic in unified files
3. Add backend-specific dependencies
4. Update CLI configuration
5. Add comprehensive tests

## Troubleshooting

### Common Issues

1. **Backend not detected**: Check `BACKEND_TYPE` environment variable
2. **Import errors**: Ensure conditional imports are properly structured
3. **Database connection issues**: Verify backend-specific connection strings
4. **Model validation errors**: Check backend-specific model definitions

### Debug Commands

```bash
# Check current backend
echo $BACKEND_TYPE

# Test database connection
python -c "from app.db.database import get_db; print('Database OK')"

# Verify model loading
python -c "from app.models.user import User; print('Models OK')"
```