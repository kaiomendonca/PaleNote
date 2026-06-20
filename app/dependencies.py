from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal
from app.services.invoice_service import InvoiceService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        db = AsyncSessionLocal()
        yield db
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close()


def get_invoice_service(db: Annotated[AsyncSession, Depends(get_db)]) -> InvoiceService:
    return InvoiceService(db)
