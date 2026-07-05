# PAI Ticket Engine

AI-powered ticket analytics platform built for enterprise operations teams.

---

## Overview

PAI Ticket Engine allows operations engineers to analyze thousands of incidents using natural language instead of SQL.

Instead of manually filtering tickets, users can ask questions like:

> Show P1 incidents assigned to Billing yesterday

or

> Which assignment group has the highest number of open incidents?

The system converts these requests into structured filters, retrieves matching tickets, and generates actionable insights.

---

## Features

- Natural language ticket search
- AI-powered query parsing
- High-performance filtering engine
- Analytics endpoints
- Ticket summarization
- Configurable dataset store
- REST API using FastAPI
- Modular architecture
- Production logging
- Comprehensive tests

---

## Architecture

```text
Frontend (Next.js)
        │
FastAPI REST API
        │
Ticket Engine
        │
Filter Engine
        │
Dataset Store
        │
CSV / Database
```

---

## Tech Stack

Python

FastAPI

Pandas

Pydantic

OpenAI

Pytest

---

## Installation

```bash
git clone ...

cd pai-ticket-engine

python -m venv .venv

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

## Running Tests

```bash
pytest
```

---

## API

GET /health

POST /query

POST /analytics

POST /insights

---

## Project Structure

app/

core/

engine/

api/

tests/

config/

---

## Roadmap

- Production frontend
- Authentication
- Semantic Search
- PostgreSQL
- Docker
- Azure deployment
- AI Insights

---

## License

MIT