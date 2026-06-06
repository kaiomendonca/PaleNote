import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class InvoiceStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Invoice(Base):
    __tablename__ = "invoces"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    access_key: Mapped[str] = mapped_column(String(44), unique=True, index=True)

    issuer_cnpj: Mapped[str] = mapped_column(String(14), index=True)

    issuer_name: Mapped[str] = mapped_column(
        String(255),
    )

    recipient_document: Mapped[str] = mapped_column(String(14))

    items: Mapped[dict] = mapped_column(JSONB)

    total_value: Mapped[float] = mapped_column(Numeric(12, 2))

    status: Mapped[InvoiceStatus] = mapped_column(
        default=InvoiceStatus.PENDING, index=True
    )

    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    update_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class InvoiceEvent(Base):
    __tablename__ = "invoice_events"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    invoice_id: Mapped[str] = mapped_column(String(36), index=True)

    status: Mapped[str] = mapped_column(String(20))

    message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
