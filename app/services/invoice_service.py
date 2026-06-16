from fastapi import UploadFile
from sqlalchemy.orm import Session


class InvoiceService:
    def __init__(self, db: Session):
        self.db = db

    async def process_xml(self, file: UploadFile):
        pass
