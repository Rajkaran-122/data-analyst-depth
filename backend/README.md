# Data Analyst Depth Portal - Production Backend

Enterprise-grade backend for the Data Analyst Depth Portal with PostgreSQL, Redis, JWT authentication, and production-ready infrastructure.

## 🚀 Features

### Phase 1: Database & Persistence
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Alembic database migrations
- ✅ Connection pooling for scalability
- ✅ All data models (User, Dataset, Workspace, Report, Query, Activity)

### Phase 2: Authentication & Authorization
- ✅ JWT-based authentication
- ✅ User registration and login
- ✅ Refresh token mechanism
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (Admin/User)

### Phase 3: Security Hardening
- ✅ Rate limiting with SlowAPI
- ✅ Input validation with Pydantic v2
- ✅ API key encryption with Fernet
- ✅ Security headers middleware
- ✅ CORS configuration

### Phase 4: Performance & Caching
- ✅ Redis caching integration
- ✅ Response compression (Gzip)
- ✅ Database query optimization with indexes

### Phase 5: Observability
- ✅ Prometheus metrics endpoint
- ✅ Structured logging
- ✅ Health check endpoints

### Phase 6: Deployment
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ Nginx reverse proxy configuration

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

## 🛠 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/Rajkaran-122/data-analyst-depth.git
cd data-analyst-depth/backend

# Copy environment file
cp .env.example .env

# Edit .env with your settings (especially GOOGLE_API_KEY)
nano .env

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

The API will be available at `http://localhost:8000`

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your settings
# Make sure PostgreSQL and Redis are running

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── database.py             # Database setup
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependencies (auth, db)
│   │   ├── auth.py             # Authentication routes
│   │   ├── dashboard.py        # Dashboard routes
│   │   └── datasets.py         # Dataset routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py         # JWT, hashing, encryption
│   │   └── exceptions.py       # Custom exceptions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── dataset.py
│   │   ├── workspace.py
│   │   ├── report.py
│   │   ├── query.py
│   │   ├── settings_model.py
│   │   ├── activity.py
│   │   └── refresh_token.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── user.py
│   │   ├── dataset.py
│   │   ├── workspace.py
│   │   ├── report.py
│   │   └── settings_schema.py
│   └── services/
│       ├── __init__.py
│       ├── auth_service.py
│       └── cache_service.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 20260127_001_initial.py
├── alembic.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── init.sql
└── .env.example
```

## 🔐 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Logout (revoke token) |
| GET | `/api/auth/profile` | Get current user profile |
| PUT | `/api/auth/profile` | Update profile |
| POST | `/api/auth/change-password` | Change password |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Get KPI statistics |
| GET | `/api/dashboard/charts/queries?range=7d` | Query trend chart |
| GET | `/api/dashboard/charts/sources` | Data sources chart |
| GET | `/api/dashboard/activity?limit=10` | Recent activity |
| GET | `/api/dashboard/summary` | Full dashboard summary |

### Datasets
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/datasets` | List datasets |
| POST | `/api/datasets` | Upload dataset |
| GET | `/api/datasets/{id}` | Get dataset |
| DELETE | `/api/datasets/{id}` | Delete dataset |
| GET | `/api/datasets/{id}/preview` | Preview data |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/metrics` | Prometheus metrics |
| GET | `/api/docs` | Swagger UI (dev only) |

## ⚙️ Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment mode | `development` |
| `DEBUG` | Enable debug mode | `true` |
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | JWT signing secret | Required (min 32 chars) |
| `GOOGLE_API_KEY` | Google Gemini API key | Optional |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `MAX_UPLOAD_SIZE` | Max file upload size | `52428800` (50MB) |

## 🗄 Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## 🐳 Docker Commands

```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (data)
docker-compose down -v

# Start with monitoring (Flower)
docker-compose --profile monitoring up -d
```

## 📊 Monitoring

- **Health Check**: `http://localhost:8000/api/health`
- **Metrics**: `http://localhost:8000/api/metrics`
- **API Docs**: `http://localhost:8000/api/docs` (dev only)
- **Flower**: `http://localhost:5555` (if monitoring profile enabled)

## 🔒 Security Best Practices

1. **Change default secrets** in production:
   - `JWT_SECRET_KEY`
   - `ENCRYPTION_KEY`
   - Database passwords

2. **Enable HTTPS** in production with Nginx SSL configuration

3. **Use environment-specific** `.env` files

4. **Regular security updates** for dependencies

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## 📚 API Documentation

When running in development mode, access:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI JSON: `http://localhost:8000/api/openapi.json`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details
