<div align="center">
  <img src="docs/logo.svg" alt="FastAPI Template CLI" width="600"/>
  
  <br/>
  
  [![PyPI version](https://badge.fury.io/py/fastapi-template-cli.svg)](https://badge.fury.io/py/fastapi-template-cli)
  [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
  
  <br/>
  
  **🚀 Production-ready FastAPI scaffolding with SQLAlchemy & MongoDB support**
  
  <br/>
  
  [📖 Documentation](#-quick-start) • [🔧 Installation](#-installation) • [🎯 Templates](#-templates) • [🗄️ Backends](#-backend-options) • [🤝 Contributing](#-contributing)
  
</div>

---

## ✨ Features

<div align="center">

| 🏗️ **Templates** | 🗄️ **Databases** | 🛡️ **Security** | 🐳 **DevOps** |
|:----------------:|:----------------:|:----------------:|:-------------:|
| **3 Templates** | **2 Backends** | **JWT Auth** | **Docker** |
| Minimal → Full-stack | SQLAlchemy + MongoDB | FastAPI Users | CI/CD Ready |

</div>

<br/>

### 🎯 **Template Options**

| Template | Purpose | Features | Best For |
|----------|---------|----------|----------|
| **🟢 Minimal** | Learning & Prototyping | Single file, basic setup | Beginners, quick demos |
| **🟡 API Only** | REST APIs & Microservices | Modular structure, testing | APIs, microservices |
| **🔵 Full-Stack** | Production Applications | Docker, migrations, auth | Production deployments |

### 🗄️ **Backend Support**

<div align="center">

| **SQLAlchemy** | **Beanie (MongoDB)** |
|:--------------:|:--------------------:|
| PostgreSQL 🐘 | MongoDB 🍃 |
| MySQL 🐬 | Async/await ⚡ |
| SQLite 📱 | JSON Schema ✅ |
| Alembic 🔄 | Aggregation 📊 |

</div>

---

## 🚀 Quick Start

### 📦 Installation

```bash
# From PyPI (recommended)
pip install fastapi-template-cli

# From source
git clone https://github.com/Sohail342/fastapi-template.git
cd cli-tool && pip install -e .
```

### ⚡ Create Your First Project

```bash
# Create a production-ready API
fastapi-template new ecommerce-api --template fullstack --backend sqlalchemy

# MongoDB-powered analytics API
fastapi-template new analytics-api --template api_only --backend beanie

# Simple microservice
fastapi-template new user-service --template api_only --backend sqlalchemy
```

### 🛠️ Development Setup

```bash
cd your-project-name
pip install -r requirements.txt

# SQLAlchemy: Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

---

## 📋 CLI Reference

### 🔧 Command Structure

```bash
fastapi-template new PROJECT_NAME [OPTIONS]
```

### ⚙️ Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--template` | `minimal`, `api_only`, `fullstack` | `minimal` | Project template type |
| `--backend` | `sqlalchemy`, `beanie` | `sqlalchemy` | Database backend |
| `--auth` | flag | - | Include authentication setup |

### 🎯 Usage Examples

```bash
# Full-stack with PostgreSQL
fastapi-template new ecommerce-api --template fullstack --backend sqlalchemy

# API-only with MongoDB
fastapi-template new analytics-api --template api_only --backend beanie

# Minimal with SQLite
fastapi-template new simple-api --template minimal --backend sqlalchemy

# With authentication
fastapi-template new social-app --template fullstack --backend beanie --auth
```

---

## 🗄️ Backend Configuration

### 🐘 **SQLAlchemy Backend**

**✅ Features:**
- PostgreSQL, MySQL, SQLite support
- SQLAlchemy 2.0+ ORM
- Alembic migrations
- Connection pooling
- Transaction support

**📦 Dependencies:**
```
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.0  # PostgreSQL
# or
pymysql>=1.1.0         # MySQL
```

**⚙️ Environment:**
```bash
DATABASE_URL=postgresql://user:password@localhost/dbname
# or
DATABASE_URL=sqlite:///./app.db
```

### 🍃 **Beanie Backend (MongoDB)**

**✅ Features:**
- MongoDB with async/await
- Beanie ODM
- JSON Schema validation
- Automatic indexing
- Aggregation pipelines

**📦 Dependencies:**
```
beanie>=1.23.0
motor>=3.3.0
pymongo>=4.6.0
```

**⚙️ Environment:**
```bash
DATABASE_URL=mongodb://localhost:27017/your_db_name
```

---

## 🏗️ Project Structure

### SQLAlchemy Backend
```
📁 ecommerce-api/
├── 📄 app/
│   ├── 📁 api/
│   │   └── api_v1/
│   │       └── endpoints/
│   │           ├── users.py
│   │           └── items.py
│   ├── 📁 crud/
│   │   ├── user.py
│   │   └── item.py
│   ├── 📁 db/
│   │   ├── database.py
│   │   └── base.py
│   ├── 📁 models/
│   │   ├── user.py
│   │   └── item.py
│   ├── 📁 schemas/
│   │   ├── user.py
│   │   └── item.py
│   └── 📄 main.py
├── 📁 tests/
├── 📄 requirements.txt
├── 📄 Dockerfile
├── 📄 docker-compose.yml
└── 📄 .env.example
```

### Beanie Backend
```
📁 analytics-api/
├── 📄 app/
│   ├── 📁 api/
│   ├── 📁 crud/
│   ├── 📁 db/
│   ├── 📁 models/
│   ├── 📁 schemas/
│   └── 📄 main.py
├── 📁 tests/
└── 📄 requirements.txt
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_users.py -v
```

---

## 🐳 Docker Support

### Quick Start with Docker

```bash
# Build and run with Docker
docker-compose up --build

# Or run standalone
docker build -t my-api .
docker run -p 8000:8000 my-api
```

### Docker Compose Services

| Service | Port | Description |
|---------|------|-------------|
| **app** | 8000 | FastAPI application |
| **db** | 5432 | PostgreSQL database |
| **redis** | 6379 | Redis cache |

---

## 🛠️ Development

### 🔧 Setup Development Environment

```bash
git clone https://github.com/Sohail342/fastapi-template.git
cd cli-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
ruff format .
ruff check .
```

### 📝 Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Security (auto-generated if empty)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

---

## 🚨 Troubleshooting

### 🔍 Common Issues

#### Database Connection
```bash
# PostgreSQL
sudo service postgresql start
psql -c "CREATE DATABASE myapp;"

# MongoDB
sudo service mongod start
mongosh --eval "use myapp;"
```

#### Migration Issues
```bash
# Reset migrations (SQLAlchemy)
alembic downgrade base
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

#### Import Errors
```bash
# Ensure all dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

### 📞 Getting Help

- **🐛 Issues**: [GitHub Issues](https://github.com/Sohail342/fastapi-template/issues)
- **📖 Docs**: [Generated README.md](README.md) in your project
- **💬 Discussions**: [GitHub Discussions](https://github.com/Sohail342/fastapi-template/discussions)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### 🔄 Contribution Workflow

1. **Fork & Clone**
   ```bash
   git clone https://github.com/Sohail342/fastapi-template.git
   cd cli-tool
   ```

2. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -e ".[dev]"
   ```

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **Make Changes**
   - Add new templates/backends
   - Update documentation
   - Add comprehensive tests

5. **Test Your Changes**
   ```bash
   pytest
   # Test template generation
   fastapi-template new test-project --template fullstack --backend sqlalchemy
   ```

6. **Submit PR**
   ```bash
   git commit -m "Add amazing feature"
   git push origin feature/amazing-feature
   ```

### 🎯 Contribution Ideas

- **🆕 New Backends**: Django ORM, Tortoise ORM, Prisma
- **🧩 New Templates**: GraphQL API, Microservices, Serverless
- **🎨 UI Templates**: React frontend, Vue.js integration
- **🔧 Tools**: Database seeders, API documentation generators

### 📋 Guidelines

- ✅ Follow PEP 8 style guidelines
- ✅ Add tests for new features
- ✅ Update documentation
- ✅ Ensure all tests pass
- ✅ Use meaningful commit messages

---

## 📊 Stats & Badges

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/fastapi-template-cli?style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fastapi-template-cli?style=flat-square)
![GitHub stars](https://img.shields.io/github/stars/Sohail342/fastapi-template?style=flat-square)
![GitHub forks](https://img.shields.io/github/forks/Sohail342/fastapi-template?style=flat-square)

</div>

---

## 🏆 Showcase

### Built with FastAPI Template CLI

<div align="center">

| **Project** | **Template** | **Backend** | **Description** |
|-------------|--------------|-------------|-----------------|
| **E-commerce API** | Full-stack | SQLAlchemy | Production e-commerce backend |
| **Analytics Service** | API Only | Beanie | Real-time data analytics |
| **User Management** | API Only | SQLAlchemy | Microservice architecture |

</div>

---

<div align="center">

**Made with ❤️ by the FastAPI community**

⭐ **Star us on GitHub** to support development!

</div>