from app.core.app_exception import AppException


class InvoiceNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            detail="Invoice not found", error_code="INVOICE_NOT_FOUND", status_code=500
        )
