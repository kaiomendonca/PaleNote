from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice


class InvoiceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_invoice(self, data: Invoice) -> Invoice:
        self.db.add(data)
        await self.db.flush()

        return data

    async def get_invoice_by_access_key(self, access_key: str) -> Invoice | None:
        statement = select(Invoice).where(Invoice.access_key == access_key)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()
