from app.core.app_exception import AppExceptionError


class InvoiceNotFoundExceptionError(AppExceptionError):
    def __init__(self):
        super().__init__(
            detail="Invoice not found", error_code="INVOICE_NOT_FOUND", status_code=500
        )
