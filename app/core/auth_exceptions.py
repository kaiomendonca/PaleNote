from app.core.app_exception import AppExceptionError


class InvalidCredentialsError(AppExceptionError):
    def __init__(self):
        super().__init__(
            detail="Invalid credentials",
            error_code="INVALID_CREDENTIALS",
            status_code=401,
        )


class InvalidTokenError(AppExceptionError):
    def __init__(self):
        super().__init__(
            detail="Invalid or missing token",
            error_code="INVALID_TOKEN",
            status_code=401,
        )


class TokenExpiredError(AppExceptionError):
    def __init__(self):
        super().__init__(
            detail="Token has expired",
            error_code="TOKEN_EXPIRED",
            status_code=401,
        )


class AccessDeniedError(AppExceptionError):
    def __init__(self):
        super().__init__(
            detail="Access denied",
            error_code="ACCESS_DENIED",
            status_code=403,
        )
