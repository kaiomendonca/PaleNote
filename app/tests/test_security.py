from datetime import datetime, timedelta, timezone

import jwt as pyjwt
import pytest
from jwt.utils import base64url_encode

from app.core.auth_exceptions import InvalidTokenError, TokenExpiredError
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TestAccessToken:
    def test_create_and_decode_returns_valid_payload(self):
        token = create_access_token("user-id-123")
        payload = decode_token(token)

        assert payload["sub"] == "user-id-123"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_exp_is_in_the_future(self):
        token = create_access_token("user-id-123")
        payload = decode_token(token)

        exp_datetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        assert exp_datetime > datetime.now(timezone.utc)


class TestRefreshToken:
    def test_create_and_decode_returns_valid_payload(self):
        token = create_refresh_token("user-id-123")
        payload = decode_token(token)

        assert payload["sub"] == "user-id-123"
        assert payload["type"] == "refresh"
        assert "jti" in payload

    def test_jti_is_unique_per_token(self):
        token_a = create_refresh_token("user-id-123")
        token_b = create_refresh_token("user-id-123")

        payload_a = decode_token(token_a)
        payload_b = decode_token(token_b)

        assert payload_a["jti"] != payload_b["jti"]

    def test_refresh_expires_much_later_than_access(self):
        access_token = create_access_token("user-id-123")
        refresh_token = create_refresh_token("user-id-123")

        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)

        assert refresh_payload["exp"] > access_payload["exp"]


class TestTokenErrors:
    def test_decode_expired_token_raises_token_expired_error(self):
        payload = {
            "sub": "user-id",
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        }
        expired_token = pyjwt.encode(
            payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        with pytest.raises(TokenExpiredError):
            decode_token(expired_token)

    def test_decode_tampered_token_raises_invalid_token_error(self):
        token = create_access_token("user-id")
        tampered = token[:-5] + "XXXXX"

        with pytest.raises(InvalidTokenError):
            decode_token(tampered)

    def test_decode_token_with_wrong_secret_raises_invalid_token_error(self):
        fake_key = "/p7+yf+E+nio+ENVxkihNaM9VtbBQN5RyN4niW0P6OY="
        payload = {
            "sub": "user-id",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        wrong_token = pyjwt.encode(payload, fake_key, algorithm="HS256")

        with pytest.raises(InvalidTokenError):
            decode_token(wrong_token)

    def test_decode_empty_string_raises_invalid_token_error(self):
        with pytest.raises(InvalidTokenError):
            decode_token("")

    def test_decode_random_string_raises_invalid_token_error(self):
        with pytest.raises(InvalidTokenError):
            decode_token("not-a-real-token")

    def test_decode_token_with_wrong_algorithm_raises_invalid_token_error(self):
        header = base64url_encode(b'{"alg":"none","typ":"JWT"}').decode()
        payload_b64 = base64url_encode(b'{"sub":"user-id","exp":9999999999}').decode()
        invalid_token = f"{header}.{payload_b64}."

        with pytest.raises(InvalidTokenError):
            decode_token(invalid_token)
