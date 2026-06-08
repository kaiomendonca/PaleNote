# PaleNote

PaleNote is a FastAPI-based API for electronic invoice (NF-e) processing, CPF/CNPJ validation, PDF generation, and asynchronous task execution with Celery.

## Overview

The project is in its early structural phase, with a FastAPI application ready to evolve through business routes, PostgreSQL integration, Redis caching, and automation through GitHub Actions.

The project name refers to the idea of preserving fiscal documents in digital form while keeping their data reliable, traceable, and accessible.

## Current stack

- Python 3.12
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic and Pydantic Settings
- PostgreSQL
- Redis
- Celery
- Poetry
- Pytest
- Ruff
- Taskipy
- Docker / Docker Compose

## Project structure

- app/main.py: FastAPI application entry point
- app/core/: configuration, logger, lifespan, and main utilities
- app/database/: database connection and session handling
- app/models/: ORM models
- app/repositories/: data access layer
- app/routers/: application routes (still under development)
- app/services/: business logic and integrations
- app/tests/: automated tests
- .github/workflows/: CI/CD with GitHub Actions

## Running locally

### 1. Install Poetry

If you do not have Poetry installed yet, use one of the options below:

```bash
python -m pip install --user poetry
```

Or, for the official installer:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Verify the installation:

```bash
poetry --version
```

### 2. Install dependencies

```bash
poetry install --with dev
```

### 3. Configure environment variables

Create a `.env` file with the required variables, using `.env.example` as a reference.

Minimal example:

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/db
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### 4. Run the API

```bash
poetry run task dev
```

The application will be available at:

- http://localhost:8000/docs

## Running with Docker

```bash
docker compose up --build
```

This command starts the API and the PostgreSQL database defined in `docker-compose.yml`.

## Logging behavior

The application uses a custom logger configured in `app/core/logger.py`.

### How it works

- `LOG_LEVEL` controls the minimum severity level that will be emitted.
- `ENVIRONMENT` determines the formatter used for the console output.

### Development mode

When `ENVIRONMENT=development` (or any value other than `production`), the logger uses `colorlog`.

This produces colored console output, which makes it easier to distinguish between:

- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

### Production mode

When `ENVIRONMENT=production`, the logger uses `python-json-logger`.

This outputs structured JSON logs to the console, which is better for log aggregation systems, monitoring tools, and production observability.

### Practical behavior

- In local development, you will see readable and colored logs.
- In production, the logs are emitted in JSON format for easier parsing and analysis.

## Tests and quality

### Run tests

```bash
poetry run task test
```

### Run lint

```bash
poetry run task lint
```

### Format code

```bash
poetry run task format
```

## Current status

The project already includes:

- the base structure of the FastAPI API
- PostgreSQL integration
- test and lint setup
- Docker containerization

It is still evolving in terms of business endpoints, which are being structured in the routes and services.

## Important note

Some routes and service files are present as the initial project structure and can still be filled with the main business logic as development progresses.