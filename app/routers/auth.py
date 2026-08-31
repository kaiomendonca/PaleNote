from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies import get_auth_service
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RevokeTokenRequest,
    TokenPairResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenPairResponse,
    summary="Authenticate a user and return tokens",
)
async def login(
    payload: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenPairResponse:
    return await service.authenticate(payload.document, payload.password)


@router.post(
    "/refresh",
    response_model=TokenPairResponse,
    summary="Rotate the refresh token for a new token pair",
)
async def refresh(
    payload: RefreshRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenPairResponse:
    return await service.refresh(payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a refresh token",
)
async def logout(
    payload: RevokeTokenRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    await service.logout(payload.refresh_token)
