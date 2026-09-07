import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.auth_exceptions import (
    AccessDeniedError,
    InvalidTokenError,
    TokenExpiredError,
)
from app.core.config import settings
from app.core.security import create_access_token
from app.dependencies import get_current_active_user, get_current_user
from app.models.users import PersonType, UserRole, Users


def make_repository_mock() -> MagicMock:
    repository = MagicMock()
    repository.get_by_id = AsyncMock()
    return repository


def make_user(**overrides) -> Users:
    defaults = {
        "id_": "user-id",
        "name": "Test User",
        "password_hash": "hash",
        "email": "user@example.com",
        "person_type": PersonType.INDIVIDUAL,
        "role": UserRole.USER,
        "document": "12345678909",
        "created_at": datetime.now(timezone.utc),
        "is_active": True,
    }
    defaults.update(overrides)
    return Users(**defaults)


def make_expired_token(user_id: str) -> str:
    import jwt as pyjwt

    payload = {
        "sub": user_id,
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    return pyjwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


class TestGetCurrentUser:
    def test_returns_user_for_valid_token(self):
        repository = make_repository_mock()
        user = make_user()
        repository.get_by_id.return_value = user
        token = create_access_token("user-id")

        result = asyncio.run(
            get_current_user(access_token=token, repository=repository)
        )

        assert result is user

    def test_returns_user_ignoring_active_state(self):
        repository = make_repository_mock()
        user = make_user(is_active=False)
        repository.get_by_id.return_value = user
        token = create_access_token("user-id")

        result = asyncio.run(
            get_current_user(access_token=token, repository=repository)
        )

        assert result is user


class TestGetCurrentUserErrors:
    def test_raises_when_invalid_token(self):
        repository = make_repository_mock()

        with pytest.raises(InvalidTokenError):
            asyncio.run(
                get_current_user(access_token="not-a-token", repository=repository)
            )

    def test_raises_when_expired_token(self):
        repository = make_repository_mock()

        with pytest.raises(TokenExpiredError):
            asyncio.run(
                get_current_user(
                    access_token=make_expired_token("user-id"), repository=repository
                )
            )

    def test_raises_when_user_not_found(self):
        repository = make_repository_mock()
        repository.get_by_id.return_value = None
        token = create_access_token("user-id")

        with pytest.raises(InvalidTokenError):
            asyncio.run(get_current_user(access_token=token, repository=repository))


class TestGetCurrentActiveUser:
    def test_returns_user_when_active(self):
        user = make_user()

        result = asyncio.run(get_current_active_user(user=user))

        assert result is user

    def test_raises_when_user_inactive(self):
        user = make_user(is_active=False)

        with pytest.raises(AccessDeniedError):
            asyncio.run(get_current_active_user(user=user))
