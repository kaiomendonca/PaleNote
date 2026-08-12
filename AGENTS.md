# AGENTS.md

## Overview
FastAPI backend for Brazilian NF-e (electronic invoice) processing: CPF/CNPJ validation, async Celery/Redis jobs, and DANFE PDF generation. Python 3.12, Poetry, async SQLAlchemy, Pydantic v2. Business/domain rules and coding standards live in `.github/copilot/skills/` (architecture.md, business-rules.md, coding-standards.md, testing-guidelines.md) — read these before implementing features.

## Commands
Run everything through Poetry + Taskipy:
- Dev server: `poetry run task dev` (uvicorn, reload, port 8000, docs at `/docs`)
- Tests: `poetry run task test` (pytest; fast, ~28 tests)
- Lint: `poetry run task lint` (ruff check)
- Format: `poetry run task format` (ruff format)
- CI runs `lint` then `test` (`.github/workflows/quality-and-tests.yml`). Pre-commit runs `ruff --fix`, `ruff-format`, then the full test suite — so make tests pass before committing.

## Required setup
`app/core/config.py` loads only `DATABASE_URL`, `LOG_LEVEL`, `ENVIRONMENT` from `.env` (extra vars like `REDIS_URL`, `SECRET_KEY` are ignored for now). All three are required at import time — even unit tests fail without a `.env` containing them. Copy from `.env.example`; the local `.env` is gitignored.

## Architecture
Strict layered layout in `app/`: `routers/` (thin HTTP) → `services/` (business logic) → `repositories/` (DB access) → `models/` (SQLAlchemy ORM). Never touch the DB from routers; never put business logic in routers. Use dependency injection (`app/dependencies.py` provides `get_db`; sessions commit/rollback/close automatically).

DB is async SQLAlchemy (`app/database/session.py`). Workers may use sync sessions, API code must not.

### Scaffolding vs. live code (do not assume these work)
- Only `app/routers/health.py` is registered in `app/main.py`. `invoices.py`, `validation.py`, and `pdf.py` routers exist but are NOT included; `validation.py` and `pdf.py` are empty.
- `app/celery_app.py` is empty; `app/workers/tasks.py` is scaffolding. No real Celery/Redis worker flow exists yet.
- `app/routers/invoices.py` upload endpoint and `InvoiceService.process_xml` are stubs that just log and return a message.

## Testing quirks
- No real DB needed and no pytest-asyncio: async code is tested with `asyncio.run()` and mocked `AsyncSession` objects (see `app/tests/test_user_repository.py`).
- `testpaths = ["app/tests"]` is set in pyproject.toml; run a single test with `poetry run pytest app/tests/test_validators.py`.

## Conventions
- Ruff: line-length 88, selects `E,F,I,B`, double quotes.
- Models use `id_` (not `id`) for UUID PKs (see `app/models/users.py`).
- Git history uses conventional-style prefixes (`feature:`, `refactor:`, `exceptions:`, `logs:`).
- Names and code are in English; domain strings (statuses, error messages) may be Portuguese.
