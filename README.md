# DSA Tracker

A containerized web app for tracking progress through data structures and algorithms topics.

## Quick Start

```bash
docker-compose up --build
```

Open [http://localhost:8080](http://localhost:8080)

## Features

- Phase/week/day navigation with sticky sidebar
- Checkbox tracking (AJAX — no page reloads)
- Reflection notes per day block (auto-saves)
- Progress bar
- Difficulty badges (Easy / Medium / Hard)
- Direct links to every problem and resource
- Full-text search across all topics and problems
- Light/dark mode toggle

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask 3 + SQLAlchemy |
| Database | PostgreSQL 16 |
| Server | Gunicorn |
| Frontend | Jinja2 + Vanilla JS |
| Deployment | Docker Compose |

## Structure

```
├── docker-compose.yml
├── .env.example
└── app/
    ├── app.py          # Flask routes
    ├── models.py       # SQLAlchemy models
    ├── seed.py         # Idempotent DB seed
    ├── templates/
    └── static/
```

## Commands

```bash
docker-compose up --build        # start
docker-compose down              # stop (keeps data)
docker-compose down -v           # stop + wipe database
docker-compose restart web       # reload after code changes
```

## Customisation

Add content by editing `app/seed.py`, then:

```bash
docker-compose restart web
```
