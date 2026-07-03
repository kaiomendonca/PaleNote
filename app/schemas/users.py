from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.users import PersonType
from app.schemas.validators import DocumentValidator


class UserCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Individual or company name",
    )

    password: str = Field(
        ..., min_length=8, max_length=128, description="user password"
    )

    email: EmailStr = Field(..., description="User Email")

    document: str = Field(
        ...,
        min_length=11,
        max_length=14,
        description="Individual taxpayer ID (CPF) or corporate taxpayer ID (CNPJ)",
    )

    @field_validator
    @classmethod
    def validate_documents(cls, value: str) -> str:
        return DocumentValidator.validate_document(value)


class UserResponse(BaseModel):
    id_: str = Field(alias="id", serialization_alias="id")

    name: str

    email: EmailStr

    person_type: PersonType

    document: str

    created_at: datetime


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    email: Optional[EmailStr] = None
    document: Optional[str] = Field(None, min_length=11, max_length=14)


class ChangePassword(BaseModel):
    current_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)
