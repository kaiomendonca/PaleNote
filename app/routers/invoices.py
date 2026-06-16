from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from app.dependencies import get_invoice_service
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/invoice", tags=["invoices"])


@router.post("/upload")
async def upload_xml(
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
    file: Annotated[UploadFile, File(...)],
) -> InvoiceService:
    return service.process_xml(file)
