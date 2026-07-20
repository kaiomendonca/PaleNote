from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.logging import get_logger
from app.dependencies import get_invoice_service
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/invoice", tags=["invoices"])
logger = get_logger(__name__)


@router.post("/upload")
async def upload_xml(
    service: Annotated[InvoiceService, Depends(get_invoice_service)],
    file: Annotated[UploadFile, File(...)],
) -> InvoiceService:
    logger.info("Invoice upload endpoint called", extra={"file_name": file.filename})
    return await service.process_xml(file)
