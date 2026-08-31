from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    document: str = Field(
        ...,
        min_length=11,
        max_length=18,
        description="Individual taxpayer ID (CPF) or corporate taxpayer ID (CNPJ)",
    )

    password: str = Field(
        ..., min_length=8, max_length=128, description="User password"
    )


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="The refresh token to rotate")


class RevokeTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="The refresh token to revoke")
