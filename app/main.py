from fastapi import FastAPI

from app.core.app_exception import AppExceptionError
from app.core.handlers import app_exception_handler
from app.core.lifespan import lifespan
from app.core.logging import configure_logging
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router

configure_logging()

openapi_tags = [
    {
        "name": "invoices",
        "description": (
            "Submit, retrieve, and cancel electronic invoices (NF-e). "
            "PDF processing is performed asynchronously through Celery."
        ),
    },
    {
        "name": "pdf",
        "description": (
            "Download the generated DANFE PDF. The file is available "
            "only when the invoice status is `COMPLETED`."
        ),
    },
    {
        "name": "validation",
        "description": (
            "Standalone validation of Brazilian tax documents. "
            "CNPJ validation results are cached in Redis for 24 hours."
        ),
    },
    {
        "name": "health",
        "description": ("API and dependency health status (PostgreSQL and Redis)."),
    },
    {
        "name": "auth",
        "description": "User authentication and token management.",
    },
]

app = FastAPI(
    title="PaleNote API",
    description=(
        "REST API for receiving, validating, processing, and "
        "storing electronic invoice data. Supports CPF/CNPJ "
        "validation, asynchronous processing, PDF generation, "
        "and document downloads."
    ),
    version="0.1.0",
    lifespan=lifespan,
    openapi_tags=openapi_tags,
    contact={
        "name": "Kaio Rodrigo de Mendonça Cardoso",
        "email": "kaiomendonca.dev@hotmail.com",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_exception_handler(AppExceptionError, app_exception_handler)

app.include_router(health_router)
app.include_router(auth_router)
