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
        query_result = MagicMock()
        query_result.scalar_one_or_none.return_value = existing_user
        db.execute.return_value = query_result

        asyncio.run(repository.update_password("user-id", "new_hash"))

        assert existing_user.password_hash == "new_hash"
        db.execute.assert_awaited_once()
        actual_query = db.execute.await_args.args[0]
        expected_query = select(Users).where(Users.id_ == "user-id")
        assert str(actual_query) == str(expected_query)
