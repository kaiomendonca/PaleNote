import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy import select

from app.models.users import Users
from app.repositories.user_repository import UserRepository


def make_async_session_mock() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    return session


class TestUserRepository:
    def test_create_user_adds_object_and_flushes(self):
        db = make_async_session_mock()
        repository = UserRepository(db)
        user_data = SimpleNamespace(name="Test User")

        result = asyncio.run(repository.create_user(user_data))

        assert result is user_data
        db.add.assert_called_once_with(user_data)
        db.flush.assert_awaited_once()

    def test_get_by_document_executes_query_and_returns_user(self):
        db = make_async_session_mock()
        repository = UserRepository(db)
        expected_user = SimpleNamespace(document="12345678901")
        query_result = MagicMock()
        query_result.scalar_one_or_none.return_value = expected_user
        db.execute.return_value = query_result

        actual_user = asyncio.run(repository.get_by_document("12345678901"))

        assert actual_user is expected_user
        db.execute.assert_awaited_once()
        actual_query = db.execute.await_args.args[0]
        expected_query = select(Users).where(
            Users.document == "12345678901",
            Users.is_active.is_(True),
        )
        assert str(actual_query) == str(expected_query)

    def test_get_by_email_executes_query_and_returns_user(self):
        db = make_async_session_mock()
        repository = UserRepository(db)
        expected_user = SimpleNamespace(email="test@example.com")
        query_result = MagicMock()
        query_result.scalar_one_or_none.return_value = expected_user
        db.execute.return_value = query_result

        actual_user = asyncio.run(repository.get_by_email("test@example.com"))

        assert actual_user is expected_user
        db.execute.assert_awaited_once()
        actual_query = db.execute.await_args.args[0]
        expected_query = select(Users).where(
            Users.email == "test@example.com",
            Users.is_active.is_(True),
        )
        assert str(actual_query) == str(expected_query)

    def test_update_password_updates_password_hash(self):
        db = make_async_session_mock()
        repository = UserRepository(db)
        existing_user = SimpleNamespace(password_hash="old_hash")

        asyncio.run(repository.update_password(existing_user, "new_hash"))

        assert existing_user.password_hash == "new_hash"
        db.execute.assert_not_awaited()

    def test_list_all_returns_only_active_users(self):
        db = make_async_session_mock()
        repository = UserRepository(db)
        users = [SimpleNamespace(name="Alice"), SimpleNamespace(name="Bob")]
        query_result = MagicMock()
        query_result.scalars.return_value.all.return_value = users
        db.execute.return_value = query_result

        result = asyncio.run(repository.list_all())

        assert result == users
        db.execute.assert_awaited_once()
        actual_query = db.execute.await_args.args[0]
        expected_query = select(Users).where(Users.is_active.is_(True))
        assert str(actual_query) == str(expected_query)

    def test_update_user_applies_only_provided_fields(self):
        db = make_async_session_mock()
        repository = UserRepository(db)
        user = SimpleNamespace(name="Old Name", email="old@example.com", document="111")

        result = asyncio.run(
            repository.update_user(
                user,
                {"name": "New Name", "email": "new@example.com"},
            )
        )

        assert result is user
        assert user.name == "New Name"
        assert user.email == "new@example.com"
        assert user.document == "111"
        db.execute.assert_not_awaited()

    def test_delete_user_sets_is_active_false(self):
        db = make_async_session_mock()
        repository = UserRepository(db)
        user = SimpleNamespace(is_active=True)

        asyncio.run(repository.delete_user(user))

        assert user.is_active is False
        db.execute.assert_not_awaited()
