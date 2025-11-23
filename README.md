# Swappo Backend - FastAPI Hello World

A simple FastAPI application with a Hello World endpoint.

## Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- On Windows:
```bash
venv\Scripts\activate
```
- On macOS/Linux:
```bash
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

### Option 1: Docker (Recommended for Production)

With Docker and PostgreSQL:
```bash
docker-compose up --build
```

Or on Windows:
```powershell
.\start-docker.ps1
```

### Option 2: Local Development

Start the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

> **Note**: Without `DATABASE_URL` environment variable, the app uses in-memory storage. Set `DATABASE_URL` to use PostgreSQL.

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints


## Testing


pytest tests/test_auth.py -v

## Api Shema 
python -c "import json; from app.main import app; print(json.dumps(app.openapi(), indent=2))" > api_schema.json