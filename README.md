# AI Task Manager API

A production-ready REST API built with **FastAPI**, **MySQL**, and **Google Gemini 2.5 Flash** for intelligent task management with AI-powered enrichment, priority scoring, and daily briefings.

## Features

- **Full CRUD** — Create, list (with filters), update, delete tasks
- **AI Task Enrichment** — Gemini auto-generates task descriptions, suggests priority, recommends deadlines
- **AI Priority Scorer** — Re-evaluates task urgency on a 1–10 scale with risk analysis
- **AI Daily Briefing** — Natural language summary of your workload with focus recommendations
- **Filtering & Pagination** — Filter tasks by status/priority, paginated responses
- **Postman Collection** — Included for all endpoints

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.111 |
| Database | MySQL + SQLAlchemy ORM |
| AI | Google Gemini 2.5 Flash |
| Validation | Pydantic v2 |
| Testing | Pytest + HTTPX |

## Project Structure

```
ai-task-manager/
├── app/
│   ├── main.py               # App entry point, middleware, router registration
│   ├── core/
│   │   ├── config.py         # Pydantic settings, env vars
│   │   └── database.py       # SQLAlchemy engine + session
│   ├── models/
│   │   └── task.py           # Task ORM model (enums, AI fields)
│   ├── schemas/
│   │   └── task.py           # Task create/update/response schemas
│   ├── routers/
│   │   ├── tasks.py          # /tasks/* CRUD endpoints
│   │   └── ai.py             # /ai/* Gemini-powered endpoints
│   └── services/
│       └── gemini_service.py # All Gemini API calls
└── tests/
    └── test_api.py           # Pytest integration tests
```

## Setup

### 1. Clone & install

```bash
git clone https://github.com/Shiv7823/ai-task-manager.git
cd ai-task-manager
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your MySQL credentials and Gemini API key
```

Get a free Gemini API key at: https://aistudio.google.com/app/apikey

### 3. Create MySQL database

```sql
CREATE DATABASE ai_task_manager;
```

Tables are auto-created on first run via SQLAlchemy.

### 4. Run

```bash
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## API Endpoints

### Tasks
| Method | Endpoint | Description |
|---|---|---|
| POST | `/tasks/` | Create task |
| GET | `/tasks/` | List tasks (filter by status, priority) |
| GET | `/tasks/{id}` | Get single task |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |

### AI Features
| Method | Endpoint | Description |
|---|---|---|
| POST | `/ai/enrich/{task_id}` | AI enriches existing task — description, priority, deadline, summary |
| POST | `/ai/enrich-new` | Get AI suggestions before creating a task |
| GET | `/ai/score/{task_id}` | Urgency score (1-10) + risk analysis |
| GET | `/ai/daily-briefing` | Natural language daily workload summary |

## Recommended Test Flow

1. `POST /tasks/` — create a task with just a title
2. `POST /ai/enrich/{id}` — Gemini fills description, priority, deadline
3. `GET /ai/score/{id}` — get urgency score with reasoning
4. `GET /ai/daily-briefing` — get full AI summary of all active tasks
5. `PUT /tasks/{id}` — update status to in_progress or done
6. `DELETE /tasks/{id}` — remove task

## Running Tests

```bash
pytest tests/ -v
```

## Resume Bullets

```
▸ Built a production-ready REST API with FastAPI and MySQL — full CRUD with
  status/priority filtering and pagination across 9 endpoints.

▸ Integrated Google Gemini 2.5 Flash for AI task enrichment: auto-generates
  descriptions, suggests priority levels with reasoning, recommends deadlines,
  and produces daily natural-language workload briefings.

▸ Structured codebase with modular routers, Pydantic v2 schemas, SQLAlchemy ORM,
  and environment-based config; endpoint coverage via Pytest + HTTPX.
```