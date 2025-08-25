# Pharma DRF Identity & Domain Service — Comprehensive Guide

This document is an in-depth, educational walkthrough of the project. It explains what the system does, why certain design choices were made, and how to extend it. Use it as a learning companion and a reference.

---

## 1) What You’re Building

An opinionated, production-style Django REST Framework (DRF) service demonstrating:

- Authentication with JWT (access/refresh tokens, blacklist)
- Role-Based Access Control (RBAC) via a custom `User` model
- Observability: request correlation IDs, structured logging
- Performance primitives: caching via Redis (ready), ORM hygiene
- Audit hooks foundation (middleware stub + logger channel)
- API documentation (OpenAPI/Swagger/Redoc)
- Containerization (Docker) and local DX (Makefile)

It also scaffolds “domain apps” to model a simple pharma manufacturing context:

- `sites` (manufacturing sites)
- `batches` (production batches, linked to sites)
- `serializations` (serial numbers per batch)
- `inspections` (QA results per batch)

---

## 2) Repository Tour

- `config/`
  - `settings.py` — DRF, JWT, CORS, caching, logging, security headers
  - `urls.py` — Admin, schema, docs, app routers
  - `wsgi.py`/`asgi.py` — entrypoints
- `core/`
  - `utils.py` — request IP/user agent helpers
  - `middleware.py` — `RequestIDMiddleware` attaches `X-Request-ID`
  - `exceptions.py` — central DRF exception handler stub
  - `permissions.py` — coarse-grained RBAC guards (Admin/QA/Operator)
- `accounts/`
  - `models.py` — custom `User` and `UserSession`
  - `serializers.py` — JWT serializer with user payload, profile & password change
  - `views.py` — login/refresh/logout/profile/password/sessions APIs
  - `urls.py` — auth endpoints
  - `admin.py` — registrations for Django admin
- `audit/`
  - `middleware.py` — request logging stub to `audit` logger
  - `urls.py` — reserved for future endpoints
- `sites/`, `batches/`, `serializations/`, `inspections/`
  - minimal `models.py` + empty `urls.py` — ready for CRUD ViewSets
- `Dockerfile`, `docker-compose.yml` — containerized dev stack
- `Makefile` — convenience commands
- `README.md` — quick start + endpoint list
- `Documentation.md` — this guide

---

## 3) How Authentication Works

### 3.1 Tokens

- The project uses `djangorestframework-simplejwt`.
- Access token lifetime: 60 minutes; refresh: 7 days
- Refresh token rotation and blacklisting are enabled for security

### 3.2 Login Flow

1. Client POSTs `username` and `password` to `/api/auth/token/`
2. On success, response has `access`, `refresh`, and a `user` object
3. Middleware records `X-Request-ID`; app logs success to `audit` channel
4. A `UserSession` record is created if a Django session key exists

Example:

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"pass"}'
```

### 3.3 Refresh & Logout

- Refresh: `POST /api/auth/token/refresh/` with `{ "refresh": "..." }`
- Logout: `POST /api/auth/logout/` optionally with `{ "refresh_token": "..." }`
  - Blacklists the refresh token and marks sessions inactive

### 3.4 Profile & Password

- `GET /api/auth/profile/` — current user
- `PUT/PATCH /api/auth/profile/update/` — update fields like `first_name`
- `POST /api/auth/password/change/` — change password (validates current + strength)

### 3.5 Securing Other Endpoints

- DRF’s default permission is `IsAuthenticated` (see `REST_FRAMEWORK` in `settings.py`)
- Add fine-grained checks using methods on `User` or `core.permissions`

---

## 4) RBAC (Role-Based Access Control)

The custom `User` model (`accounts.models.User`) adds a `role` field with choices:

- `admin` — full control
- `qa` — quality assurance actions
- `operator` — day-to-day operational actions

Convenience helpers:

- `user.is_admin`, `user.is_qa`, `user.is_operator`
- `can_access_audit_logs`, `can_modify_sites`, `can_modify_batches`, etc.

You can enforce RBAC in views:

```python
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdmin

class SomeView(APIView):
    permission_classes = [IsAuthenticated & IsAdmin]
```

Or by checking `request.user` in the action itself if logic is subtle.

---

## 5) Observability & Audit

### 5.1 Request Correlation

- `core.middleware.RequestIDMiddleware` ensures each request has a unique `X-Request-ID` header in the response; upstream proxies can set their own.

### 5.2 Logging

- `settings.py` defines structured formatters; a dedicated `audit` logger is configured
- The `audit.middleware.AuditMiddleware` attaches lightweight request context and logs on each response

Extending audit:

- Add a proper `AuditLog` model
- Hook Django signals (`post_save`, `post_delete`) to capture before/after diffs
- Build read-only audit endpoints in `audit/urls.py` + views

---

## 6) Performance & Caching

- Redis cache backend is configured; keys/TTLs are set in `CACHE_TTL`
- Apply caching strategically:
  - Function-based: `from django.views.decorators.cache import cache_page`
  - Per-viewset list/retrieve: override methods + use cache API
- ORM hygiene:
  - Use `select_related`/`prefetch_related` for relational reads
  - Add DB indexes (examples in models)

---

## 7) API Documentation (OpenAPI)

- Schema: `GET /api/schema/`
- Swagger UI: `GET /api/docs/`
- Redoc: `GET /api/redoc/`
- Decorate views with `@extend_schema` to clarify parameters and responses

---

## 8) Running the Project

### 8.1 Docker (recommended)

Prereqs: Docker Desktop running

```bash
make dev
# or
docker-compose up --build
```

Services:

- `db` — Postgres 15
- `redis` — Redis 7
- `web` — Django runserver on 8000

Environment variables are taken from compose service `web` and your local `.env`.

### 8.2 Local (SQLite fallback)

If Docker isn’t available, you can still run migrations with SQLite:

1) Install Python deps directly (quick path):

```bash
pip install Django djangorestframework djangorestframework-simplejwt django-filter drf-spectacular python-decouple django-redis psycopg2-binary
```

2) Run migrations and start the server:

```bash
set USE_SQLITE=1
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://localhost:8000/`.

---

## 9) Adding CRUD for Domain Models (Hands-on)

This project includes models but not full CRUD yet — ideal for learning.

Example: add CRUD for `sites.Site`:

1) Create `sites/serializers.py`:

```python
from rest_framework import serializers
from .models import Site

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = '__all__'
```

2) Create `sites/views.py`:

```python
from rest_framework import viewsets, permissions
from .models import Site
from .serializers import SiteSerializer

class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all().order_by('name')
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]
```

3) Wire routes in `sites/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiteViewSet

router = DefaultRouter()
router.register('', SiteViewSet, basename='site')

urlpatterns = [
    path('', include(router.urls)),
]
```

Repeat similarly for `batches`, `serializations`, `inspections`.

RBAC tip: override `get_permissions()` in viewsets to branch by action and role.

---

## 10) Testing Strategy

Recommended layers:

- Unit tests for serializers and permissions
- API tests for auth flows and CRUD
- Performance checks for key endpoints (P95 targets in plan)

Run tests:

```bash
make test        # dockerized
pytest           # local
```

Coverage is configured via `pyproject.toml`.

---

## 11) CI/CD Sketch

Use GitHub Actions to ensure quality on every PR:

- Steps: setup Python, install deps, lint (ruff/black/mypy), run tests, publish coverage
- Optional: build and push Docker image on `main` tags

Minimal workflow example (create `.github/workflows/ci.yml`):

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -U pip
      - run: pip install Django djangorestframework djangorestframework-simplejwt django-filter drf-spectacular python-decouple django-redis psycopg2-binary ruff black mypy pytest pytest-django pytest-cov
      - run: |
          export USE_SQLITE=1
          python manage.py makemigrations --check --dry-run || true
          python manage.py migrate --noinput
          pytest --cov=. --cov-report=term-missing
```

---

## 12) Deployment Notes

- Prefer Postgres and Redis in production
- Use a real WSGI/ASGI server (gunicorn/uvicorn) behind Nginx or a load balancer
- Set `DEBUG=False`, configure `ALLOWED_HOSTS`, secure cookies, HTTPS, HSTS
- Rotate `SECRET_KEY`, use environment variables (12-factor)

Example command for gunicorn (Docker CMD):

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
```

---

## 13) Security Checklist

- JWT refresh rotation + blacklist enabled
- Strong password validation
- Sensitive data not logged
- CORS restricted for production
- CSRF/SameSite/Secure cookies set appropriately
- Security headers: X-Frame-Options, HSTS (when `DEBUG=False`)

Consider:

- Rate limiting tweaks for sensitive endpoints
- Admin IP allowlists and 2FA on admin accounts
- Secret scanning and dependency updates

---

## 14) Troubleshooting

- Docker cannot connect: ensure Docker Desktop is running
- `ModuleNotFoundError: django`: install deps (`pip install Django ...`)
- Migrations issues: delete `db.sqlite3` locally and re-migrate if using SQLite
- Swagger not loading: ensure `drf-spectacular` is installed and `DEFAULT_SCHEMA_CLASS` is set

---

## 15) Roadmap Ideas (from the plan)

- Full audit trail: immutable `AuditLog`, before/after diffs, masking
- ViewSets + filters + ordering + pagination for all domain apps
- Caching strategy and invalidation per domain
- Performance tests and P95 latency tracking
- Pre-commit hooks (ruff/black/mypy) and GitHub Actions CI
- OAuth2 integration and API versioning

---

## 16) Learning Path Suggestions

1. Read through `accounts/` to understand JWT and session tracking
2. Build CRUD for `sites` using the hands-on steps above
3. Add RBAC per action (`create` only for admins, etc.)
4. Enable caching for the most-read endpoints and measure impact
5. Add a minimal `AuditLog` model and record changes via signals
6. Wire a CI workflow and enforce linters

By completing the steps above, you’ll have practiced real production patterns while keeping the scope manageable.


