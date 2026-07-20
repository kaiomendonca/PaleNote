from app.core.app_exception import AppExceptionError


class IncorrectPasswordError(AppExceptionError):
    def __init__(self):
        super().__init__(
            detail="The password must have at least 8 characters,"
            "an uppercase letter, a lowercase letter, and a number.",
            error_code="INCORRECT_PASSWORD",
            status_code=400,
        )
