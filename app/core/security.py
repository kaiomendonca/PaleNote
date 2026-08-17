import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.auth_exceptions import InvalidTokenError, TokenExpiredError
from app.core.config import settings
from app.core.user_exceptions import InvalidPasswordError


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_matches = bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        password_matches = False

    if not password_matches:
        raise InvalidPasswordError()

    return True


def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "type": "access",
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "exp": datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# =============================================================================
# Função de validação/decodificação de token
# =============================================================================
#
# jwt.decode() faz 3 coisas automaticamente:
#
# 1. Verifica a ASSINATURA: recria o HMAC-SHA256(header + payload, SECRET_KEY)
#    e compara com a assinatura que veio no token. Se forem diferentes →
#    alguém alterou o token → InvalidSignatureError (subclass de InvalidTokenError).
#
# 2. Verifica a EXPIRAÇÃO: se o campo "exp" do payload é anterior ao momento
#    atual → ExpiredSignatureError (subclass de InvalidTokenError).
#
# 3. Retorna o payload como dict: {"sub": "user-id", "type": "access", "exp": ...}
#
# Tratamos as exceções separadamente para retornar mensagens mais específicas
# ao frontend (token expirado vs token inválido). Ambas resultam em 401, mas
# o frontend pode distinguir — por exemplo, mostrar "faça login novamente"
# para token expirado, ou "sessão inválida" para token adulterado.
#
# algorithms=[settings.JWT_ALGORITHM]:
#   PyJWT exige que você liste explicitamente os algoritmos aceitos.
#   Isso é uma medida de segurança: se alguém tentar forjar um token
#   com algoritmo "none" (sem assinatura), o PyJWT rejeita porque
#   "none" não está na lista de aceitos.


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError() from None
    except jwt.InvalidTokenError:
        raise InvalidTokenError() from None
