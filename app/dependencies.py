from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_exceptions import AccessDeniedError, InvalidTokenError
from app.core.security import decode_token
from app.database.session import AsyncSessionLocal
from app.models.users import Users
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.invoice_service import InvoiceService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        db = AsyncSessionLocal()
        yield db
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close()


def get_invoice_service(db: Annotated[AsyncSession, Depends(get_db)]) -> InvoiceService:
    return InvoiceService(db)


def get_user_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_refresh_token_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)


def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    refresh_token_repository: Annotated[
        RefreshTokenRepository, Depends(get_refresh_token_repository)
    ],
) -> AuthService:
    return AuthService(user_repository, refresh_token_repository)


async def get_current_user(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> Users:
    payload = decode_token(access_token)
    user = await repository.get_by_id(payload["sub"])
    if not user:
        raise InvalidTokenError()
    return user


async def get_current_active_user(
    user: Annotated[Users, Depends(get_current_user)],
) -> Users:
    if not user.is_active:
        raise AccessDeniedError()
    return user
