from datetime import datetime, timezone

from app.core.auth_exceptions import (
    AccessDeniedError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.core.user_exceptions import InvalidPasswordError
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPairResponse


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def authenticate(self, document: str, password: str) -> TokenPairResponse:
        user = await self.user_repository.get_by_document(document)
        if not user:
            raise InvalidCredentialsError()

        try:
            verify_password(password, user.password_hash)
        except InvalidPasswordError:
            raise InvalidCredentialsError() from None

        if not user.is_active:
            raise AccessDeniedError()

        token = create_refresh_token(user.id_)
        payload = decode_token(token)
        await self.refresh_token_repository.register_refresh_token(
            jti=payload["jti"],
            user_id=user.id_,
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )

        return TokenPairResponse(
            access_token=create_access_token(user.id_),
            refresh_token=token,
        )

    async def refresh(self, refresh_token: str) -> TokenPairResponse:
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise InvalidTokenError()

        jti = payload.get("jti")
        if not jti:
            raise InvalidTokenError()

        stored_token = await self.refresh_token_repository.get_for_update_by_jti(jti)
        if not stored_token or stored_token.revoked:
            raise InvalidTokenError()

        expires_at = stored_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise InvalidTokenError()

        user = await self.user_repository.get_by_id(payload["sub"])
        if not user or not user.is_active:
            raise InvalidTokenError()

        await self.refresh_token_repository.revoke_by_jti(jti)

        new_token = create_refresh_token(user.id_)
        new_payload = decode_token(new_token)
        await self.refresh_token_repository.register_refresh_token(
            jti=new_payload["jti"],
            user_id=user.id_,
            expires_at=datetime.fromtimestamp(new_payload["exp"], tz=timezone.utc),
        )

        return TokenPairResponse(
            access_token=create_access_token(user.id_),
            refresh_token=new_token,
        )

    async def logout(self, refresh_token: str) -> None:
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise InvalidTokenError()

        jti = payload.get("jti")
        if not jti:
            raise InvalidTokenError()

        await self.refresh_token_repository.revoke_by_jti(jti)
