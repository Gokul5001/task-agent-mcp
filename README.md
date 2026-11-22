# task-agent-mcp

A small task-tracking API for an agent workflow: an agent picks up GitHub issues labeled `agent-task`, looks up data through tools, and reports back. This repo currently contains the API service (Task A). The MCP server and agent runner come next. See `docs/spec.md` for the full design.

## What it does
- Stores one task per GitHub issue (duplicate issues return the existing task).
- REST endpoints: `POST /tasks`, `GET /tasks` (filter by status), `GET /tasks/{id}`, `PATCH /tasks/{id}`, `GET /health`.
- Finished tasks (`done` or `failed`) cannot change status (HTTP 409).

## Stack
FastAPI, SQLAlchemy, PostgreSQL (SQLite for tests), pytest, Docker.

## Run the tests
    python -m venv .venv
    source .venv/Scripts/activate    # Windows Git Bash; use .venv/bin/activate on Linux/macOS
    pip install -r requirements.txt
    pytest

Tests use in-memory SQLite, so Docker is not needed.

## Run locally
    uvicorn app.main:app --reload
Then open http://127.0.0.1:8000/docs

## Run with Docker (API + PostgreSQL)
    docker compose up --build
The API listens on port 8000. The database password in docker-compose.yml is for development only. Change it before any real deployment.

## How this was built
The base API, tests and Docker files were generated with an AI assistant from my written spec (`docs/spec.md`). I reviewed and ran everything, and added the finished-task rule and its test myself. Notes on what broke and how I fixed it are in `docs/log.md`.

## Status
- [x] Task A: API service
- [ ] Task B: MCP server
- [ ] Task C: Agent runner and deployment