# FastAPI Template

A powerful CLI tool for generating production-ready FastAPI projects with best practices, integrated authentication, and flexible ORM options.

## Features

- 🚀 **Production Ready**: Pre-configured with security, logging, and deployment best practices
- 🔐 **Integrated Authentication**: FastAPI-Users integration with JWT authentication
- 🗄️ **Flexible ORM**: Choose between SQLAlchemy (PostgreSQL) or Beanie (MongoDB)
- 🐳 **Docker Support**: Complete Docker setup with docker-compose
- 📦 **Celery Integration**: Background task processing (fullstack projects)
- 🧪 **Testing Ready**: Pre-configured testing setup
- 📊 **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- 🎯 **CLI Driven**: Simple command-line interface for project generation

## Quick Start

### Installation

```bash
pip install fastapi-template
```

### Create a New Project

```bash
# Create an API-only project with SQLAlchemy
fastapi-template new my-api --orm sqlalchemy --type api

# Create a fullstack project with MongoDB
fastapi-template new my-app --orm beanie --type fullstack

# Create with custom description
fastapi-template new my-project --orm sqlalchemy --type fullstack \
  --description "My awesome FastAPI project" --author "Your Name"
```

## Project Types

### API-Only Projects
- Lightweight FastAPI backend
- Database integration (SQLAlchemy or Beanie)
- FastAPI-Users authentication
- No frontend or background tasks

### Fullstack Projects
- Complete backend with FastAPI
- Database integration
- FastAPI-Users authentication
- Celery for background tasks
- Redis for caching and task queue
- Docker setup with docker-compose

## ORM Options

### SQLAlchemy (PostgreSQL)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0 with async support
- **Migrations**: Alembic
- **Connection**: asyncpg driver

### Beanie (MongoDB)
- **Database**: MongoDB
- **ODM**: Beanie (async MongoDB ODM)
- **Driver**: Motor
- **Schema**: Pydantic-based documents

## Usage

### Basic Commands

```bash
# List available templates
fastapi-template list-templates

# Create a new project
fastapi-template new myproject

# Show version
fastapi-template version
```

### Project Structure

Generated projects follow a clean architecture:

```
myproject/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py
│   │       └── endpoints/
│   │           └── users.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── session.py (SQLAlchemy) or mongo.py (Beanie)
│   │   └── base_class.py (SQLAlchemy)
│   ├── models/
│   │   └── user.py
│   ├── schemas/
│   │   └── user.py
│   ├── users.py (FastAPI-Users config)
│   └── main.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml (fullstack only)
├── alembic/ (SQLAlchemy only)
├── workers/ (fullstack only)
├── pyproject.toml
├── .env
└── .gitignore
```

## Development

### SQLAlchemy Projects

1. **Setup Database**
   ```bash
   cd myproject
   pip install -e .
   alembic upgrade head
   ```

2. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Create Database Migration**
   ```bash
   alembic revision --autogenerate -m "Add new table"
   ```

### Beanie Projects

1. **Setup MongoDB**
   ```bash
   cd myproject
   pip install -e .
   # MongoDB will auto-initialize on first connection
   ```

2. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload
   ```

### Fullstack Projects (Docker)

1. **Start All Services**
   ```bash
   cd myproject
   docker-compose up -d
   ```

2. **Access Services**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MongoDB: localhost:27017 (Beanie)
   - PostgreSQL: localhost:5432 (SQLAlchemy)
   - Redis: localhost:6379

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname  # SQLAlchemy
MONGODB_URL=mongodb://localhost:27017/myproject  # Beanie

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (fullstack)
REDIS_URL=redis://localhost:6379/0

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

### Database Configuration

#### SQLAlchemy (PostgreSQL)
```bash
# Install PostgreSQL
# Create database
createdb myproject

# Set DATABASE_URL
export DATABASE_URL=postgresql+asyncpg://user:password@localhost/myproject
```

#### Beanie (MongoDB)
```bash
# Install MongoDB
# MongoDB will create database on first connection
export MONGODB_URL=mongodb://localhost:27017/myproject
```

## API Endpoints

Generated projects include these endpoints:

### Authentication
- `POST /auth/jwt/login` - User login
- `POST /auth/jwt/logout` - User logout
- `POST /auth/register` - User registration
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password

### Users
- `GET /users/me` - Get current user
- `PATCH /users/me` - Update current user
- `GET /users/{id}` - Get user by ID
- `GET /users` - List users (admin only)

### Health Check
- `GET /health` - API health status
- `GET /` - Welcome message

## Testing

Generated projects include testing setup:

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_users.py
```

## Deployment

### Docker Deployment

For fullstack projects:

```bash
# Build and run
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment

1. **Environment Variables**
   ```bash
   export SECRET_KEY=your-production-secret
   export DATABASE_URL=your-production-db-url
   ```

2. **Gunicorn/Uvicorn**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

3. **Nginx Reverse Proxy**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `pytest`
6. Commit your changes: `git commit -am 'Add feature'`
7. Push to the branch: `git push origin feature-name`
8. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://github.com/your-org/fastapi-template/wiki)
- 🐛 [Issue Tracker](https://github.com/your-org/fastapi-template/issues)
- 💬 [Discussions](https://github.com/your-org/fastapi-template/discussions)

## Changelog

### v1.0.0
- Initial release
- SQLAlchemy and Beanie support
- API-only and fullstack project types
- FastAPI-Users integration
- Docker support
- CLI tool