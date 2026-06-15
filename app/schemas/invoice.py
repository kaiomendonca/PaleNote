from decimal import Decimal

from pydantic import BaseModel, Field


class InvoiceItem(BaseModel):
    description: str = Field(min_length=1, max_length=255)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0)


class InvoiceCreate(BaseModel):
    access_key: str = Field(min_length=44, max_length=44)

    issuer_cnpj: str = Field(min_length=14, max_length=14)

    issuer_name: str = Field(min_length=1, max_length=255)

    recipient_document: str = Field(min_length=11, max_length=14)

    items: list[InvoiceItem]
