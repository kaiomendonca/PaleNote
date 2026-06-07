from fastapi import FastAPI

from app.core.lifespan import lifespan

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
