from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.dependencies import get_current_active_user
from app.main import app
from app.models.users import PersonType, UserRole, Users


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


def make_client(active_user: Users | None) -> TestClient:
    app.dependency_overrides[get_current_active_user] = lambda: active_user
    return TestClient(app)


def teardown_function():
    app.dependency_overrides.clear()


class TestGetMe:
    def test_get_me_returns_authenticated_user(self):
        client = make_client(make_user())

        response = client.get("/users/me")

        assert response.status_code == 200
        assert response.json()["id_"] == "user-id"
        assert response.json()["name"] == "Test User"

    def test_get_me_returns_401_when_not_authenticated(self):
        app.dependency_overrides.clear()
        client = TestClient(app)

        response = client.get("/users/me")

        assert response.status_code == 401
