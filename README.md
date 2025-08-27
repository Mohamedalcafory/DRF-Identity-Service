# DRF Identity Service

A Django REST Framework-based identity and authentication service with role-based access control and audit logging.

## 🚀 Features

- User authentication and authorization
- Role-based access control 
- Audit logging
- PostgreSQL database
- Redis caching
- Docker containerization

## 🛠️ Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL
- Redis

## 🏃‍♂️ Quick Start

1. Clone the repository and setup environment:
```bash
git clone <repository-url>
cd DRF-Identity-Service
# Copy environment file (create .env.example if it doesn't exist)
```

2. Start the development environment:
```bash
make dev
```

3. Run migrations and create superuser:
```bash
make migrate
make superuser
```

4. Access the service at http://localhost:8000/

## 🔌 API Endpoints (Auth)

- POST `/api/auth/token/` obtain access/refresh
- POST `/api/auth/token/refresh/` refresh access
- POST `/api/auth/logout/` blacklist refresh
- GET `/api/auth/profile/` current user
- PUT/PATCH `/api/auth/profile/update/` update profile
- POST `/api/auth/password/change/` change password
- GET `/api/auth/sessions/` list recent sessions
- POST `/api/auth/sessions/terminate/<id>/` terminate a session

## 🔧 Configuration

Key environment variables (see [.env](.env)):

```bash
# Django Configuration
SECRET_KEY=django-insecure-change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=drf_identity
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/1
```

## 🛠️ Development Commands

```bash
# Start development environment
make dev

# Run migrations
make migrate

# Create superuser
make superuser

# Run tests with coverage
make test

# Run linting checks
make lint

# Format code
make fmt

# Load test fixtures
make load-fixtures

# Access Django shell
make shell
```

## 🧪 Testing

Run the test suite:

```bash
make test
```

For continuous test running during development:

```bash
make test-watch
```

## 📦 Project Structure

- `config/` - Django project (settings, urls, asgi, wsgi)
- `core/` - Utilities, middleware, exceptions, permissions
- `accounts/` - User model, auth serializers/views/urls, admin
- `audit/` - Audit middleware and future endpoints
- `Dockerfile` - Container definition
- `docker-compose.yml` - Service orchestration
- `Makefile` - Development commands
- `Documentation.md` - Comprehensive guide

## 🔒 Security Features

- Password strength validation
- Role-based permissions
- Audit logging
- Secure password hashing
- Token authentication

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test: `make test lint`
4. Commit changes: `git commit -m "Add new feature"`
5. Push and create PR

## 📚 Documentation

For detailed documentation and learning guide, see [Documentation.md](Documentation.md).