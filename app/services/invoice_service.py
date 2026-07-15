from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger

logger = get_logger(__name__)


class InvoiceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_xml(self, file: UploadFile):
        logger.info("Starting XML processing", extra={"file_name": file.filename})
        logger.info("XML upload received", extra={"file_name": file.filename})

        return {"message": "XML received", "filename": file.filename}
