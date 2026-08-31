import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import jwt as pyjwt
import pytest

from app.core.auth_exceptions import (
    AccessDeniedError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
)
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
)
from app.models.refresh_token import RefreshToken
from app.models.users import PersonType, UserRole, Users
from app.services.auth_service import AuthService


def make_user_repository_mock() -> MagicMock:
    repository = MagicMock()
    repository.get_by_document = AsyncMock()
    repository.get_by_id = AsyncMock()
    return repository


def make_refresh_token_repository_mock() -> MagicMock:
    repository = MagicMock()
    repository.register_refresh_token = AsyncMock()
    repository.get_by_jti = AsyncMock()
    repository.get_for_update_by_jti = AsyncMock()
    repository.revoke_by_jti = AsyncMock()
    repository.revoke_all_for_user = AsyncMock()
    return repository


def make_user(**overrides) -> Users:
    defaults = {
        "id_": "user-id",
        "name": "Test User",
        "password_hash": hash_password("SecurePass123"),
        "email": "user@example.com",
        "person_type": PersonType.INDIVIDUAL,
        "document": "12345678909",
        "role": UserRole.USER,
        "created_at": datetime.now(timezone.utc),
        "is_active": True,
    }
    defaults.update(overrides)
    return Users(**defaults)


def make_stored_token(**overrides) -> RefreshToken:
    defaults = {
        "id_": "token-id",
        "jti": "test-jti",
        "user_id": "user-id",
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        "revoked": False,
        "created_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    token = MagicMock(spec=RefreshToken)
    for key, value in defaults.items():
        setattr(token, key, value)
    return token


def make_auth_service(
    user_repository=None, refresh_token_repository=None
) -> AuthService:
    user_repo = user_repository or make_user_repository_mock()
    refresh_repo = refresh_token_repository or make_refresh_token_repository_mock()
    return AuthService(user_repo, refresh_repo)


class TestAuthenticate:
    def test_authenticate_returns_token_pair_on_success(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        user = make_user()
        user_repo.get_by_document.return_value = user
        service = AuthService(user_repo, refresh_repo)

        result = asyncio.run(service.authenticate("12345678909", "SecurePass123"))

        assert result.token_type == "bearer"
        access_payload = decode_token(result.access_token)
        refresh_payload = decode_token(result.refresh_token)
        assert access_payload["sub"] == "user-id"
        assert access_payload["type"] == "access"
        assert refresh_payload["sub"] == "user-id"
        assert refresh_payload["type"] == "refresh"
        refresh_repo.register_refresh_token.assert_awaited_once()

    def test_authenticate_raises_when_document_not_found(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        user_repo.get_by_document.return_value = None
        service = AuthService(user_repo, refresh_repo)

        with pytest.raises(InvalidCredentialsError):
            asyncio.run(service.authenticate("12345678909", "SecurePass123"))

    def test_authenticate_raises_when_password_is_wrong(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        user = make_user()
        user_repo.get_by_document.return_value = user
        service = AuthService(user_repo, refresh_repo)

        with pytest.raises(InvalidCredentialsError):
            asyncio.run(service.authenticate("12345678909", "WrongPass123"))

    def test_authenticate_raises_when_user_is_inactive(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        user = make_user(is_active=False)
        user_repo.get_by_document.return_value = user
        service = AuthService(user_repo, refresh_repo)

        with pytest.raises(AccessDeniedError):
            asyncio.run(service.authenticate("12345678909", "SecurePass123"))

    def test_authenticate_persists_refresh_token(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        user = make_user()
        user_repo.get_by_document.return_value = user
        service = AuthService(user_repo, refresh_repo)

        result = asyncio.run(service.authenticate("12345678909", "SecurePass123"))

        refresh_payload = decode_token(result.refresh_token)
        call_kwargs = refresh_repo.register_refresh_token.call_args.kwargs
        assert call_kwargs["jti"] == refresh_payload["jti"]
        assert call_kwargs["user_id"] == "user-id"
        assert isinstance(call_kwargs["expires_at"], datetime)


class TestRefresh:
    def test_refresh_returns_new_token_pair(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        user = make_user()
        user_repo.get_by_id.return_value = user
        token = create_refresh_token("user-id")
        jti = decode_token(token)["jti"]
        stored = make_stored_token(jti=jti)
        refresh_repo.get_for_update_by_jti.return_value = stored
        service = AuthService(user_repo, refresh_repo)

        result = asyncio.run(service.refresh(token))

        assert result.token_type == "bearer"
        new_access = decode_token(result.access_token)
        new_refresh = decode_token(result.refresh_token)
        assert new_access["sub"] == "user-id"
        assert new_refresh["type"] == "refresh"
        refresh_repo.revoke_by_jti.assert_awaited_once_with(jti)
        refresh_repo.register_refresh_token.assert_awaited_once()

    def test_refresh_revokes_old_token_and_persists_new(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        user = make_user()
        user_repo.get_by_id.return_value = user
        token = create_refresh_token("user-id")
        jti = decode_token(token)["jti"]
        stored = make_stored_token(jti=jti)
        refresh_repo.get_for_update_by_jti.return_value = stored
        service = AuthService(user_repo, refresh_repo)

        result = asyncio.run(service.refresh(token))

        new_payload = decode_token(result.refresh_token)
        refresh_repo.revoke_by_jti.assert_awaited_once_with(jti)
        call_kwargs = refresh_repo.register_refresh_token.call_args.kwargs
        assert call_kwargs["jti"] == new_payload["jti"]
        assert call_kwargs["user_id"] == "user-id"
        assert isinstance(call_kwargs["expires_at"], datetime)


class TestRefreshErrors:
    def test_refresh_raises_when_token_is_expired(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        service = AuthService(user_repo, refresh_repo)
        expired_payload = {
            "sub": "user-id",
            "type": "refresh",
            "jti": "expired-jti",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        }
        expired_token = pyjwt.encode(
            expired_payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        with pytest.raises(TokenExpiredError):
            asyncio.run(service.refresh(expired_token))

    def test_refresh_raises_when_token_is_invalid(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        service = AuthService(user_repo, refresh_repo)

        with pytest.raises(InvalidTokenError):
            asyncio.run(service.refresh("not-a-valid-token"))

    def test_refresh_raises_when_token_is_not_a_refresh_token(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        service = AuthService(user_repo, refresh_repo)
        access_token = create_access_token("user-id")

        with pytest.raises(InvalidTokenError):
            asyncio.run(service.refresh(access_token))

    def test_refresh_raises_when_jti_not_in_db(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        refresh_repo.get_for_update_by_jti.return_value = None
        service = AuthService(user_repo, refresh_repo)
        token = create_refresh_token("user-id")

        with pytest.raises(InvalidTokenError):
            asyncio.run(service.refresh(token))

    def test_refresh_raises_when_token_is_revoked(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        token = create_refresh_token("user-id")
        jti = decode_token(token)["jti"]
        stored = make_stored_token(jti=jti, revoked=True)
        refresh_repo.get_for_update_by_jti.return_value = stored
        service = AuthService(user_repo, refresh_repo)

        with pytest.raises(InvalidTokenError):
            asyncio.run(service.refresh(token))

    def test_refresh_raises_when_user_not_found(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        user_repo.get_by_id.return_value = None
        token = create_refresh_token("user-id")
        jti = decode_token(token)["jti"]
        stored = make_stored_token(jti=jti)
        refresh_repo.get_for_update_by_jti.return_value = stored
        service = AuthService(user_repo, refresh_repo)

        with pytest.raises(InvalidTokenError):
            asyncio.run(service.refresh(token))

    def test_refresh_raises_when_user_is_inactive(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        user = make_user(is_active=False)
        user_repo.get_by_id.return_value = user
        token = create_refresh_token("user-id")
        jti = decode_token(token)["jti"]
        stored = make_stored_token(jti=jti)
        refresh_repo.get_for_update_by_jti.return_value = stored
        service = AuthService(user_repo, refresh_repo)

        with pytest.raises(InvalidTokenError):
            asyncio.run(service.refresh(token))

    def test_refresh_raises_when_jti_missing_from_payload(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        service = AuthService(user_repo, refresh_repo)
        payload_no_jti = {
            "sub": "user-id",
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
        }
        token = pyjwt.encode(
            payload_no_jti, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        with pytest.raises(InvalidTokenError):
            asyncio.run(service.refresh(token))


class TestLogout:
    def test_logout_revokes_token(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        service = AuthService(user_repo, refresh_repo)
        token = create_refresh_token("user-id")
        jti = decode_token(token)["jti"]

        asyncio.run(service.logout(token))

        refresh_repo.revoke_by_jti.assert_awaited_once_with(jti)

    def test_logout_raises_when_token_is_invalid(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        service = AuthService(user_repo, refresh_repo)

        with pytest.raises(InvalidTokenError):
            asyncio.run(service.logout("not-a-valid-token"))

    def test_logout_raises_when_token_is_not_a_refresh_token(self):
        user_repo = make_user_repository_mock()
        refresh_repo = make_refresh_token_repository_mock()
        service = AuthService(user_repo, refresh_repo)
        access_token = create_access_token("user-id")

        with pytest.raises(InvalidTokenError):
            asyncio.run(service.logout(access_token))
