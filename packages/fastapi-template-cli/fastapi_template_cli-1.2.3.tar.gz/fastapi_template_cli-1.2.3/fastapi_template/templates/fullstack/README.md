# FastAPI Fullstack Template

A production-ready FastAPI template with authentication, database integration, testing, and deployment configurations.

## Features

- 🔐 **Authentication & Authorization**: JWT-based authentication with role-based access control
- 🗄️ **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- 🧪 **Testing**: Comprehensive test suite with pytest and factory patterns
- 🐳 **Docker**: Docker and Docker Compose configurations
- 🔧 **Development Tools**: Pre-commit hooks, linting, formatting, and type checking
- 📊 **Monitoring**: Health check endpoints and structured logging
- 🚀 **Production Ready**: Gunicorn server, security headers, and CORS configuration

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Docker & Docker Compose (optional)

### Installation

1. **Clone and setup**:
   ```bash
   # Copy the template
   cp -r fastapi_template/templates/fullstack my-project
   cd my-project
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Database Setup**:
   ```bash
   # Create database
   createdb fastapi_fullstack
   
   # Run migrations
   alembic upgrade head
   
   # Seed initial data
   python -c "from app.db.init_db import init_db; init_db()"
   ```

4. **Run Development Server**:
   ```bash
   make dev
   # or
   uvicorn app.main:app --reload
   ```

### Using Docker

1. **Development**:
   ```bash
   make docker-up
   ```

2. **Production**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application factory
│   ├── api/                    # API routes and endpoints
│   │   ├── v1/
│   │   │   ├── endpoints/      # API endpoints
│   │   │   └── api.py          # API router configuration
│   │   └── deps.py             # Dependencies and auth
│   ├── core/                   # Core configurations
│   │   ├── config.py           # Settings and configuration
│   │   └── security.py         # Security utilities
│   ├── crud/                   # CRUD operations
│   ├── db/                     # Database configuration
│   ├── models/                 # SQLAlchemy models
│   └── schemas/                # Pydantic schemas
├── tests/                      # Test suite
├── alembic/                    # Database migrations
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # Docker image configuration
├── Makefile                    # Development commands
└── requirements.txt            # Python dependencies
```

## API Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### Authentication Endpoints

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login

### User Endpoints

- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `POST /api/v1/users/` - Create user (admin only)
- `PUT /api/v1/users/{user_id}` - Update user

### Item Endpoints

- `GET /api/v1/items/` - Get items
- `POST /api/v1/items/` - Create item
- `GET /api/v1/items/{item_id}` - Get item by ID
- `PUT /api/v1/items/{item_id}` - Update item
- `DELETE /api/v1/items/{item_id}` - Delete item

## Development

### Available Commands

```bash
make help              # Show all available commands
make install          # Install dependencies
make dev              # Run development server
make test             # Run tests
make test-cov         # Run tests with coverage
make lint             # Run linting
make format           # Format code
make migrate          # Create migration
make upgrade          # Run migrations
make clean            # Clean cache and temporary files
```

### Code Quality

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **ruff** for linting
- **mypy** for type checking
- **pre-commit** for git hooks

Setup pre-commit hooks:
```bash
pre-commit install
```

### Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run in watch mode
pytest -f
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Run migrations
alembic upgrade head

# Downgrade migration
alembic downgrade -1

# Show migration history
alembic history
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment (development/production) | `development` |
| `SECRET_KEY` | JWT secret key | `change-me` |
| `POSTGRES_SERVER` | PostgreSQL host | `localhost` |
| `POSTGRES_USER` | PostgreSQL user | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres` |
| `POSTGRES_DB` | PostgreSQL database | `fastapi_fullstack` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `FIRST_SUPERUSER` | Initial superuser email | `admin@example.com` |
| `FIRST_SUPERUSER_PASSWORD` | Initial superuser password | `admin` |

## Deployment

### Production Deployment

1. **Environment Setup**:
   ```bash
   export ENVIRONMENT=production
   export SECRET_KEY=your-production-secret-key
   ```

2. **Docker Production**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Manual Deployment**:
   ```bash
   pip install -r requirements.txt
   alembic upgrade head
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Health Checks

The application includes health check endpoints:
- `GET /health` - Basic health check
- `GET /api/v1/health/` - Detailed health check with database connectivity

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Run linting (`make lint`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.