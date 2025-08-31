# FastAPI-Users Authentication Setup

This template uses [FastAPI-Users](https://fastapi-users.github.io/fastapi-users/) for comprehensive user management and authentication.

## Overview

FastAPI-Users provides ready-to-use user management with:
- User registration and login
- JWT authentication
- Password reset functionality
- Email verification
- User profile management
- Admin/superuser support
- Social OAuth2 (extensible)

## Backend Selection

During project creation, you can choose between:

### 1. SQLAlchemy Backend (PostgreSQL/SQLite)
- **Database**: PostgreSQL (production) or SQLite (development)
- **ORM**: SQLAlchemy 2.0+ with async support
- **Driver**: asyncpg for PostgreSQL

### 2. Beanie Backend (MongoDB)
- **Database**: MongoDB
- **ODM**: Beanie (async MongoDB ODM)
- **Driver**: motor (async MongoDB driver)

## Quick Start

### SQLAlchemy Backend

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up database**:
   ```bash
   # Create database (PostgreSQL)
   createdb fastapi_fullstack
   
   # Run migrations
   alembic upgrade head
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Start the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

### Beanie Backend (MongoDB)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MongoDB**:
   ```bash
   # Start MongoDB (if using local)
   mongod
   
   # Or use Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Set MONGODB_URL and DATABASE_NAME in .env
   ```

4. **Start the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/jwt/login` | Login with email/password |
| POST | `/auth/jwt/logout` | Logout current user |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Reset password with token |
| POST | `/auth/request-verify-token` | Request email verification |
| POST | `/auth/verify` | Verify email with token |

### User Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get current user profile |
| PATCH | `/users/me` | Update current user profile |
| GET | `/users/{id}` | Get user by ID (admin only) |
| PATCH | `/users/{id}` | Update user by ID (admin only) |
| DELETE | `/users/{id}` | Delete user by ID (admin only) |

## Configuration

### Environment Variables

#### SQLAlchemy Backend
```bash
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fastapi_fullstack

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 days

# Email (for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=your-email@gmail.com
```

#### Beanie Backend
```bash
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=fastapi_fullstack

# Security and email settings same as above
```

## Usage Examples

### User Registration

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "username": "johndoe",
    "full_name": "John Doe"
  }'
```

### User Login

```bash
curl -X POST "http://localhost:8000/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword123"
```

### Get Current User

```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Update User Profile

```bash
curl -X PATCH "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Updated Doe",
    "username": "johndoe_updated"
  }'
```

## Database Schema

### SQLAlchemy Tables
- `users`: User data with FastAPI-Users fields
- `items`: Your application-specific data
- `alembic_version`: Migration tracking

### MongoDB Collections
- `users`: User documents
- `items`: Your application-specific documents

## Migration (SQLAlchemy Only)

### Create Migration
```bash
alembic revision --autogenerate -m "Add new field"
```

### Apply Migration
```bash
alembic upgrade head
```

### Downgrade Migration
```bash
alembic downgrade -1
```

## Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

### Test Authentication

The test suite includes:
- User registration tests
- Login/logout tests
- Password reset tests
- User profile tests
- Authorization tests

## Extending FastAPI-Users

### Custom User Fields

To add custom fields to the user model:

1. **SQLAlchemy**: Edit `app/auth/models.py`
2. **Beanie**: Edit `app/auth/models_beanie.py`

### Social Authentication

FastAPI-Users supports OAuth2 providers:
- Google
- GitHub
- Facebook
- Twitter
- And many more...

### Custom Validators

Add password validators or email validators as needed.

## Security Features

- **JWT tokens**: Secure stateless authentication
- **Password hashing**: Using bcrypt
- **Rate limiting**: Built-in protection against brute force
- **CORS**: Configurable cross-origin resource sharing
- **Security headers**: Comprehensive security headers via middleware

## Troubleshooting

### Common Issues

1. **Database connection errors**:
   - Check database credentials in `.env`
   - Ensure database is running
   - Verify network connectivity

2. **JWT token issues**:
   - Check SECRET_KEY consistency
   - Verify token expiration settings
   - Ensure proper Authorization header format

3. **Migration errors**:
   - Check Alembic configuration
   - Verify database permissions
   - Review migration scripts

### Debug Mode

Enable debug logging:
```bash
export ENVIRONMENT=development
export DEBUG=True
```

## Production Deployment

### SQLAlchemy with PostgreSQL

1. **Database**: Use managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.)
2. **Environment**: Set `ENVIRONMENT=production`
3. **Secrets**: Use proper secret management (AWS Secrets Manager, etc.)
4. **SSL**: Enable SSL connections

### Beanie with MongoDB

1. **Database**: Use MongoDB Atlas or managed MongoDB
2. **Connection**: Use connection strings with authentication
3. **Security**: Enable MongoDB authentication and SSL

### Docker Deployment

See `docker-compose.yml` for both SQLAlchemy and Beanie configurations.

## Support

- **FastAPI-Users Documentation**: https://fastapi-users.github.io/fastapi-users/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Beanie Documentation**: https://beanie-odm.dev/
- **MongoDB Documentation**: https://docs.mongodb.com/

For issues specific to this template, please check the GitHub repository.