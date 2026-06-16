from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.services.invoice_service import InvoiceService


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_invoice_service(db: Annotated[Session, Depends(get_db)]) -> InvoiceService:
    return InvoiceService(db)
