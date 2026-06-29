PaleNote Architecture
Project Overview

PaleNote is an Open Source backend project focused on asynchronous processing and validation of Brazilian electronic invoices (NF-e).

The system receives XML files, validates business rules, generates DANFE PDFs and exposes processing status through an API.

Main goals:

High scalability
Low API latency
Asynchronous processing
Auditability
Fault tolerance
High Level Architecture

Flow:

User
→ FastAPI API
→ PostgreSQL (initial state persistence)
→ Redis Queue
→ Celery Workers
→ Fiscal Validation
→ DANFE Generation
→ PostgreSQL (PDF and final state storage)
→ User invoice status query endpoint

API Responsibilities

FastAPI should:

Receive one or multiple XML files.
Perform basic parsing validation.
Persist initial event data in PostgreSQL.
Publish processing events to Redis.
Return immediate HTTP response.

The API must NEVER perform heavy fiscal processing synchronously.

Database
The system uses a relational database to persist invoice records and their processing history.

A dedicated event store keeps track of state transitions over time.

The main record stores the primary invoice information and references to generated artifacts.

Redis acts exclusively as:

Broker
Queue

Queue:

A dedicated queue is used to dispatch processing jobs asynchronously.

Each message should carry the minimum information required to identify the work item and support retries.

Celery

Celery is responsible for:

Managing worker pool.
Consuming Redis messages.
Executing asynchronous tasks.
Retrying failed tasks.
Updating processing status.

Optional:

Celery Beat schedules periodic jobs.

Worker Flow

Worker steps:

Update status to processing.
Validate NF-e business rules.
Update status to validating.
Generate DANFE HTML.
Convert HTML to PDF.
Persist PDF.
Update status to completed.

If an exception occurs:

Update status to failed.
Persist error message.
Architectural Rules
Follow layered architecture.
Endpoints must remain thin.
Business rules belong to services.
Persistence belongs to repositories.
Heavy processing belongs to Celery workers.
Avoid business logic inside routes.
Prefer dependency injection.
Use asynchronous SQLAlchemy sessions inside FastAPI.
Workers may use synchronous sessions if necessary.

Project Layers

app/database
app/routers
app/services
app/repositories
app/models
app/schemas
app/core
app/workers
app/docs
app/tests

Responsibilities:

tests → tests application
routers → HTTP layer
services → business logic
repositories → database access
database → database and ORM configuration
workers → Celery tasks
core → configuration and infrastructure
schemas → DTOs
models → ORM entities
Decision Guidelines

When suggesting implementations:

Prefer asynchronous execution.
Avoid blocking the API request cycle.
Preserve audit trail.
Prioritize scalability.
Prefer explicit dependency injection.
Keep components loosely coupled.