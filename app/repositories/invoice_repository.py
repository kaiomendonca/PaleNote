from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.models.invoice import Invoice

logger = get_logger("app.db.invoice")


class InvoiceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_invoice(self, data: Invoice) -> Invoice:
        logger.info("Registering invoice", extra={"access_key": data.access_key})
        self.db.add(data)
        await self.db.flush()
        logger.info(
            "Invoice registered successfully", extra={"access_key": data.access_key}
        )

        return data

    async def get_invoice_by_access_key(self, access_key: str) -> Invoice | None:
        logger.debug("Looking up invoice", extra={"access_key": access_key})
        statement = select(Invoice).where(Invoice.access_key == access_key)
        result = await self.db.execute(statement)
        invoice = result.scalar_one_or_none()
        logger.info(
            "Invoice lookup completed",
            extra={"access_key": access_key, "found": invoice is not None},
        )
        return invoice
