# Swappo Authentication Microservice - Docker Setup

## 🐳 Quick Start with Docker

### 1. Build and run with Docker Compose:

```bash
docker-compose up --build
```

This will:
- Start a PostgreSQL database
- Build and run the FastAPI application
- Expose the API on http://localhost:8000

### 2. Stop the containers:

```bash
docker-compose down
```

### 3. Stop and remove all data:

```bash
docker-compose down -v
```

## 📋 Docker Commands

### Build the Docker image:
```bash
docker build -t swappo-api .
```

### Run with Docker (without database):
```bash
docker run -p 8000:8000 swappo-api
```

### Run with Docker (with PostgreSQL):
```bash
docker-compose up
```

### View logs:
```bash
docker-compose logs -f api
docker-compose logs -f db
```

### Access PostgreSQL database:
```bash
docker-compose exec db psql -U swappo -d swappo_auth
```

## 🔧 Environment Variables

Create a `.env` file in the project root for custom configuration:

```env
# Database
DATABASE_URL=postgresql://swappo:swappo_password@db:5432/swappo_auth

# JWT Secrets (CHANGE IN PRODUCTION!)
SECRET_KEY=your-super-secret-key-here
REFRESH_SECRET_KEY=your-refresh-secret-key-here

# Token Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=production
```

### Generate secure secrets:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📦 Docker Compose Services

### API Service
- **Container Name**: swappo_api
- **Port**: 8000
- **Image**: Built from Dockerfile
- **Depends on**: PostgreSQL database

### Database Service
- **Container Name**: swappo_postgres
- **Port**: 5432
- **Image**: postgres:15-alpine
- **Volume**: postgres_data (persistent storage)

## 🔒 Security Notes

**Important for Production:**

1. **Change default passwords** in `docker-compose.yml`
2. **Set strong JWT secrets** via environment variables
3. **Use HTTPS** with a reverse proxy (nginx, traefik)
4. **Limit CORS origins** in the app configuration
5. **Use Docker secrets** for sensitive data
6. **Enable PostgreSQL SSL** in production

## 🚀 Production Deployment

### Using Docker Swarm:

```bash
docker stack deploy -c docker-compose.yml swappo
```

### Using Kubernetes:

Convert docker-compose.yml to Kubernetes manifests:
```bash
kompose convert -f docker-compose.yml
kubectl apply -f .
```

## 🧪 Testing with Docker

Run tests in container:
```bash
docker-compose exec api pytest tests/ -v
```

## 📊 Monitoring

### Check container health:
```bash
docker-compose ps
```

### View resource usage:
```bash
docker stats
```

## 🔄 Updates and Migrations

### Rebuild after code changes:
```bash
docker-compose up --build
```

### Database migrations (if using Alembic):
```bash
docker-compose exec api alembic upgrade head
```

## 💾 Backup Database

```bash
docker-compose exec db pg_dump -U swappo swappo_auth > backup.sql
```

### Restore Database

```bash
docker-compose exec -T db psql -U swappo swappo_auth < backup.sql
```

## 🌐 API Access

Once running, access:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **OpenAPI**: http://localhost:8000/openapi.json

## 📝 Notes

- The application automatically detects if `DATABASE_URL` is set
- Without `DATABASE_URL`, it uses in-memory storage (for testing)
- With `DATABASE_URL`, it uses PostgreSQL (for production)
- Database tables are created automatically on startup
