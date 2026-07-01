from pydantic import BaseModel, EmailStr, Field


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
