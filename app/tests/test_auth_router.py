from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.dependencies import get_auth_service
from app.main import app


class FakeAuthService:
    def __init__(self):
        self.authenticate = AsyncMock()
        self.refresh = AsyncMock()
        self.logout = AsyncMock()


def make_client(service: FakeAuthService) -> TestClient:
    app.dependency_overrides[get_auth_service] = lambda: service
    client = TestClient(app)
    return client


def teardown_function():
    app.dependency_overrides.clear()


class TestLogin:
    def test_login_returns_tokens_on_success(self):
        service = FakeAuthService()
        service.authenticate.return_value = {
            "access_token": "access",
            "refresh_token": "refresh",
            "token_type": "bearer",
        }
        client = make_client(service)

        response = client.post(
            "/auth/login",
            json={"document": "12345678909", "password": "SecurePass123"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "access_token": "access",
            "refresh_token": "refresh",
            "token_type": "bearer",
        }
        service.authenticate.assert_awaited_once_with("12345678909", "SecurePass123")


class TestRefresh:
    def test_refresh_returns_tokens_on_success(self):
        service = FakeAuthService()
        service.refresh.return_value = {
            "access_token": "new-access",
            "refresh_token": "new-refresh",
            "token_type": "bearer",
        }
        client = make_client(service)

        response = client.post(
            "/auth/refresh", json={"refresh_token": "valid-refresh-token"}
        )

        assert response.status_code == 200
        assert response.json()["access_token"] == "new-access"
        service.refresh.assert_awaited_once_with("valid-refresh-token")


class TestLogout:
    def test_logout_returns_204_on_success(self):
        service = FakeAuthService()
        client = make_client(service)

        response = client.post(
            "/auth/logout", json={"refresh_token": "valid-refresh-token"}
        )

        assert response.status_code == 204
        service.logout.assert_awaited_once_with("valid-refresh-token")
