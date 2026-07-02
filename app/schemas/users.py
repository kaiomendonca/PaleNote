from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.users import PersonType


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


class UserResponse(BaseModel):
    name: str

    email: EmailStr

    person_type: PersonType

    document: str

    created_at: datetime


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    email: Optional[EmailStr] = None
    person_type: Optional[PersonType] = None
    document: Optional[str] = Field(None, min_length=11, max_length=14)


class ChangePassword(BaseModel):
    current_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)
