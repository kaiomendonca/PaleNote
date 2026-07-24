from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.users import PersonType
from app.schemas.validators import DocumentValidator, FieldValidator


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

    @field_validator("password")
    @classmethod
    def verify_password(cls, value: str) -> str:
        return FieldValidator.validate_password_characters(value)

    email: EmailStr = Field(..., description="User Email")

    document: str = Field(
        ...,
        min_length=11,
        max_length=18,
        description="Individual taxpayer ID (CPF) or corporate taxpayer ID (CNPJ)",
    )

    @field_validator("document")
    @classmethod
    def validate_documents(cls, document: str) -> str:
        return DocumentValidator.validate_document(document)


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

    @field_validator("new_password")
    @classmethod
    def verify_password(cls, value: str) -> str:
        return FieldValidator.validate_password_characters(value)

    confirm_new_password: str = Field(..., min_length=8, max_length=128)

    @model_validator(mode="after")
    def passwords_match(self) -> "ChangePassword":
        FieldValidator.checks_if_password_match(
            self.confirm_new_password, self.new_password
        )
        return self

    @model_validator(mode="after")
    def new_password_must_be_different(self) -> "ChangePassword":
        FieldValidator.new_password_must_differ(
            self.current_password, self.new_password
        )
        return self
