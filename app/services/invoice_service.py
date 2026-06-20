from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession


class InvoiceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_xml(self, file: UploadFile):
        pass
