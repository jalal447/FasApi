# FastAPI Document Manager API

Production-ready FastAPI backend with modular DDD, async SQLAlchemy, and JWT authentication.

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL (Async SQLAlchemy + asyncpg)
- **Migrations**: Alembic
- **Security**: JWT (bcrypt/passlib)
- **Testing**: Pytest

## Setup

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Variables**:
   Create a `.env` file based on the provided `.env` template.
4. **Database Migrations**:
   ```bash
   alembic upgrade head
   ```
5. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation
Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Components
- `app/core/`: Security, config, and middleware.
- `app/users/`: User management.
- `app/documents/`: Document management and advanced search.
- `app/shares/`: Sharing system and permissions.
- `app/db/`: Session management and models.
