import asyncio
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.security import hash_password, verify_password
from app.core.user_exceptions import (
    EmailAlreadyExistsError,
    InvalidDocumentError,
    InvalidPasswordError,
    UserNotFoundError,
)
from app.models.users import PersonType, Users
from app.schemas.users import ChangePassword, UserCreate, UserUpdate
from app.services.user_service import UserService


def make_repository_mock() -> MagicMock:
    repository = MagicMock()
    repository.exists_by_email = AsyncMock()
    repository.exists_by_document = AsyncMock()
    repository.create_user = AsyncMock()
    repository.get_by_document = AsyncMock()
    repository.list_all = AsyncMock()
    repository.update_user = AsyncMock()
    repository.delete_user = AsyncMock()
    repository.update_password = AsyncMock()
    return repository


def make_user(**overrides) -> Users:
    defaults = {
        "id_": "user-id",
        "name": "Test User",
        "password_hash": "hash",
        "email": "user@example.com",
        "person_type": PersonType.INDIVIDUAL,
        "document": "12345678909",
        "created_at": datetime.now(timezone.utc),
        "is_active": True,
    }
    defaults.update(overrides)
    return Users(**defaults)


def simulate_flush(user: Users) -> Users:
    user.id_ = user.id_ or str(uuid.uuid4())
    user.created_at = user.created_at or datetime.now(timezone.utc)
    return user


class TestCreateUser:
    def test_create_user_hashes_password_and_returns_response(self):
        repository = make_repository_mock()
        repository.exists_by_email.return_value = False
        repository.exists_by_document.return_value = False
        repository.create_user.side_effect = simulate_flush
        service = UserService(repository)
        payload = UserCreate(
            name="Test User",
            password="SecurePass123",
            email="user@example.com",
            document="12345678909",
        )

        result = asyncio.run(service.create_user(payload))

        created_user = repository.create_user.await_args.args[0]
        assert isinstance(result.id_, str)
        assert result.name == "Test User"
        assert result.person_type == PersonType.INDIVIDUAL
        assert created_user.password_hash != payload.password
        assert verify_password(payload.password, created_user.password_hash)

    def test_create_user_sets_company_person_type_for_cnpj(self):
        repository = make_repository_mock()
        repository.exists_by_email.return_value = False
        repository.exists_by_document.return_value = False
        repository.create_user.side_effect = simulate_flush
        service = UserService(repository)
        payload = UserCreate(
            name="Company",
            password="SecurePass123",
            email="company@example.com",
            document="11222333000181",
        )

        asyncio.run(service.create_user(payload))

        created_user = repository.create_user.await_args.args[0]
        assert created_user.person_type == PersonType.COMPANY

    def test_create_user_raises_when_email_already_exists(self):
        repository = make_repository_mock()
        repository.exists_by_email.return_value = True
        service = UserService(repository)
        payload = UserCreate(
            name="Test User",
            password="SecurePass123",
            email="user@example.com",
            document="12345678909",
        )

        with pytest.raises(EmailAlreadyExistsError):
            asyncio.run(service.create_user(payload))

        repository.create_user.assert_not_called()

    def test_create_user_raises_when_document_already_exists(self):
        repository = make_repository_mock()
        repository.exists_by_email.return_value = False
        repository.exists_by_document.return_value = True
        service = UserService(repository)
        payload = UserCreate(
            name="Test User",
            password="SecurePass123",
            email="user@example.com",
            document="12345678909",
        )

        with pytest.raises(InvalidDocumentError):
            asyncio.run(service.create_user(payload))

        repository.create_user.assert_not_called()


class TestChangePassword:
    def test_change_password_updates_user_password(self):
        repository = make_repository_mock()
        old_hash = hash_password("CurrentPass123")
        user = make_user(password_hash=old_hash)
        repository.get_by_document.return_value = user
        service = UserService(repository)
        payload = ChangePassword(
            current_password="CurrentPass123",
            new_password="NewPass456",
            confirm_new_password="NewPass456",
        )

        asyncio.run(service.change_password("12345678909", payload))

        updated_user, new_hash = repository.update_password.await_args.args
        assert updated_user is user
        assert new_hash != old_hash
        assert verify_password("NewPass456", new_hash)

    def test_change_password_raises_when_current_password_is_wrong(self):
        repository = make_repository_mock()
        user = make_user(password_hash=hash_password("CurrentPass123"))
        repository.get_by_document.return_value = user
        service = UserService(repository)
        payload = ChangePassword(
            current_password="WrongPass123",
            new_password="NewPass456",
            confirm_new_password="NewPass456",
        )

        with pytest.raises(InvalidPasswordError):
            asyncio.run(service.change_password("12345678909", payload))

        repository.update_password.assert_not_called()

    def test_change_password_raises_when_user_not_found(self):
        repository = make_repository_mock()
        repository.get_by_document.return_value = None
        service = UserService(repository)
        payload = ChangePassword(
            current_password="CurrentPass123",
            new_password="NewPass456",
            confirm_new_password="NewPass456",
        )

        with pytest.raises(UserNotFoundError):
            asyncio.run(service.change_password("12345678909", payload))


class TestGetUser:
    def test_get_user_returns_user_response(self):
        repository = make_repository_mock()
        user = make_user()
        repository.get_by_document.return_value = user
        service = UserService(repository)

        result = asyncio.run(service.get_user("12345678909"))

        assert result.id_ == "user-id"
        assert result.name == "Test User"
        assert result.email == "user@example.com"

    def test_get_user_raises_when_user_not_found(self):
        repository = make_repository_mock()
        repository.get_by_document.return_value = None
        service = UserService(repository)

        with pytest.raises(UserNotFoundError):
            asyncio.run(service.get_user("12345678909"))


class TestListUsers:
    def test_list_users_returns_user_responses(self):
        repository = make_repository_mock()
        user_1 = make_user()
        user_2 = make_user(id_="user-id-2", document="11222333000181")
        repository.list_all.return_value = [user_1, user_2]
        service = UserService(repository)

        result = asyncio.run(service.list_users())

        assert [user.id_ for user in result] == ["user-id", "user-id-2"]


class TestUpdateUser:
    def test_update_user_applies_only_provided_fields(self):
        repository = make_repository_mock()
        user = make_user(name="Old Name")
        repository.get_by_document.return_value = user

        def _apply_fields(updated_user: Users, fields: dict) -> Users:
            for key, value in fields.items():
                setattr(updated_user, key, value)
            return updated_user

        repository.update_user.side_effect = _apply_fields
        service = UserService(repository)
        payload = UserUpdate(name="New Name")

        result = asyncio.run(service.update_user("12345678909", payload))

        repository.update_user.assert_awaited_once_with(user, {"name": "New Name"})
        assert result.name == "New Name"

    def test_update_user_raises_when_email_already_exists(self):
        repository = make_repository_mock()
        user = make_user()
        repository.get_by_document.return_value = user
        repository.exists_by_email.return_value = True
        service = UserService(repository)
        payload = UserUpdate(email="other@example.com")

        with pytest.raises(EmailAlreadyExistsError):
            asyncio.run(service.update_user("12345678909", payload))

        repository.update_user.assert_not_called()

    def test_update_user_raises_when_document_already_exists(self):
        repository = make_repository_mock()
        user = make_user()
        repository.get_by_document.return_value = user
        repository.exists_by_document.return_value = True
        service = UserService(repository)
        payload = UserUpdate(document="11222333000181")

        with pytest.raises(InvalidDocumentError):
            asyncio.run(service.update_user("12345678909", payload))

        repository.update_user.assert_not_called()

    def test_update_user_raises_when_user_not_found(self):
        repository = make_repository_mock()
        repository.get_by_document.return_value = None
        service = UserService(repository)
        payload = UserUpdate(name="New Name")

        with pytest.raises(UserNotFoundError):
            asyncio.run(service.update_user("12345678909", payload))


class TestDeleteUser:
    def test_delete_user_deactivates_user(self):
        repository = make_repository_mock()
        user = make_user()
        repository.get_by_document.return_value = user
        service = UserService(repository)

        asyncio.run(service.delete_user("12345678909"))

        repository.delete_user.assert_awaited_once_with(user)

    def test_delete_user_raises_when_user_not_found(self):
        repository = make_repository_mock()
        repository.get_by_document.return_value = None
        service = UserService(repository)

        with pytest.raises(UserNotFoundError):
            asyncio.run(service.delete_user("12345678909"))
