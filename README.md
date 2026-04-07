# DSA Tracker

A free, structured tool to help developers prepare for coding interviews — built with the belief that everyone deserves access to a clear, guided path to becoming a better engineer, regardless of budget.

## Why this exists

Most DSA prep tools give you a problem list and leave you to figure out the rest. This tracker gives you a **full curriculum** — from foundations to advanced algorithms — with:

- Structured learning resources before every problem, not just problem links
- Explicit **brute-force → optimal** progression so you build real understanding, not just memorised solutions
- A projected finish date based on your actual pace, so you stay accountable
- Personal reflection notes per study session

The goal is to make structured, interview-focused DSA prep available to everyone for free.

## Quick Start

```bash
docker-compose up --build
```

Open [http://localhost:8080](http://localhost:8080)

## Features

- 5-phase main course (Foundation → Core Structures → Advanced DS → Algorithms → Practice & Mastery)
- Fast Track phases (Phases 6-7) covering the 30 most-asked interview problems with brute-force and optimal approaches
- Velocity-based projected finish date with delay indicators (green / yellow / red)
- Phase/week/day navigation with sticky sidebar
- Checkbox tracking (AJAX — no page reloads)
- Reflection notes per day block (auto-saves)
- Progress bar
- Difficulty badges (Easy / Medium / Hard)
- Direct links to every problem and resource
- Full-text search across all topics and problems
- Dark mode only. No exceptions.

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
└── app/
    ├── app.py           # Flask routes
    ├── models.py        # SQLAlchemy models
    ├── seed.py          # Idempotent DB seed
    ├── reset_dates.py   # Reset all date ranges to a new start date
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

## Resetting Course Dates

All phase, week, and day block date ranges can be reset to start from any date without touching progress (checked items, reflections, etc.).

**Reset to today:**

```bash
docker exec adamcodingcom-tracker-1 python3 /app/reset_dates.py
```

**Reset to a specific date:**

```bash
docker exec adamcodingcom-tracker-1 python3 /app/reset_dates.py 2026-09-01
```

The script recalculates the full 104-day plan (5 phases, 14 weeks, all day blocks) from the given start date and updates `CourseMeta` (`started_at` and `planned_end`) accordingly. The container name may differ if you are running the tracker standalone — check with `docker ps`.

If you need to change the course structure itself (phase lengths, block durations), edit the offset tables at the top of `app/reset_dates.py`.

## Customisation

Add or change course content by editing `app/seed.py`, then:

```bash
docker-compose restart web
```

## Roadmap

- Multi-user support with Google OAuth (each user gets their own course instance on first login)
- Public hosted version so no setup is required
