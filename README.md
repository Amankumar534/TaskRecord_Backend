# TaskRecord Backend - FastAPI + PostgreSQL

Production-ready backend boilerplate for the **TaskRecord** web application, built with **FastAPI**, **PostgreSQL**, **SQLAlchemy (Async)**, and **JWT authentication**.

---

## 🚀 Features

- **Authentication & Security**:
  - `POST /api/v1/auth/signup`: User registration with email uniqueness, full name, hashed password (bcrypt).
  - `POST /api/v1/auth/login`: Secure JWT access token generation.
  - `GET /api/v1/auth/me`: Authenticated user profile retrieval.
- **Tasks Management**:
  - `GET /api/v1/tasks/`: List user tasks with filtering (`status`, `priority`, `category`, `search`, pagination).
  - `POST /api/v1/tasks/`: Create a task with start date, end date, status, priority, category, and nested subtasks.
  - `GET /api/v1/tasks/{id}`: Detailed view of a specific task.
  - `PATCH /api/v1/tasks/{id}`: Update task properties with date validation.
  - `DELETE /api/v1/tasks/{id}`: Delete task and cascade delete its subtasks.
- **Subtasks**:
  - `POST /api/v1/tasks/{id}/subtasks`: Add a dynamic subtask to an existing task.
  - `PATCH /api/v1/tasks/{id}/subtasks/{sub_id}`: Toggle completion or update subtask title.
  - `DELETE /api/v1/tasks/{id}/subtasks/{sub_id}`: Remove subtask.
- **Dashboard & Analytics**:
  - `GET /api/v1/dashboard/stats`: Returns task completion percentage, status counts, urgent metrics, subtask progress, and breakdown by category and priority.
- **Dockerized**:
  - `Dockerfile` & `docker-compose.yml` with health-checks, automatic database setup, and live code reload.
- **CORS Configured**: Pre-configured for Next.js (`http://localhost:3000`).

---

## 📁 Project Structure

```text
Notebook_backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # Auth and DB dependencies (get_current_user, get_db)
│   │   └── v1/
│   │       ├── api.py           # V1 Router aggregator
│   │       └── endpoints/
│   │           ├── auth.py      # Signup, Login, Me endpoints
│   │           ├── tasks.py     # Tasks & Subtasks CRUD endpoints
│   │           └── dashboard.py # Dashboard statistics endpoint
│   ├── core/
│   │   ├── config.py            # Pydantic Settings & environment variables
│   │   └── security.py          # Bcrypt hashing & JWT token generators
│   ├── db/
│   │   └── session.py           # Async SQLAlchemy engine & AsyncSessionLocal
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py            # User, Task, Subtask ORM models
│   ├── schemas/
│   │   └── schemas.py           # Pydantic request & response schemas
│   └── main.py                  # FastAPI application with CORS and lifespan
├── tests/
│   └── test_api.py              # Pytest test suite
├── Dockerfile                   # Docker container configuration
├── docker-compose.yml           # Multi-container orchestration (FastAPI + PostgreSQL)
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── .env.example                 # Example configuration
└── README.md
```

---

## 🛠️ Running with Docker Compose (Recommended)

1. Make sure Docker is running on your machine.
2. In the `Notebook_backend` folder, run:

```bash
docker-compose up --build
```
*(or `docker compose up --build`)*

The FastAPI backend will start at:
- **API Base URL**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/api/v1/docs`
- **ReDoc Documentation**: `http://localhost:8000/api/v1/redoc`
- **Health Check**: `http://localhost:8000/health`

PostgreSQL will be exposed on port `5432` with credentials:
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `task_db`
- **Username**: `postgres`
- **Password**: `postgres`

---

## 💻 Running Locally (Without Docker)

### 1. Create a Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup PostgreSQL
Ensure PostgreSQL is installed and running locally, then create the database:
```sql
CREATE DATABASE task_db;
```

Update your `.env` file with your local database credentials:
```env
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=task_db
```

### 4. Run the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Running Tests
```bash
pytest
```
