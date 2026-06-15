from sqlalchemy.orm import Session

from app.models.invoice import Invoice


class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def register_invoice(self, data: Invoice) -> Invoice:
        self.db.add(data)
        self.db.flush()

        return data

    def get_invoice_by_access_key(self, access_key: str) -> Invoice | None:
        return self.db.query(Invoice).filter(Invoice.access_key == access_key).first()
