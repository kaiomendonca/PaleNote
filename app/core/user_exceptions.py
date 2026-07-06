from app.core.app_exception import AppException


class UserCreationError(AppException):
    def __init__(self):
        super().__init__(
            detail="User cannot be created",
            error_code="USER_NOT_CREATED",
            status_code=500,
        )


class UploadFailedError(AppException):
    def __init__(self):
        super().__init__(
            detail="Upload failed", error_code="UPLOAD_FAILED", status_code=500
        )


class UserInvalidError(AppException):
    def __init__(self):
        super().__init__(
            detail="Invalid e-mail", error_code="USER_INVALID_ERROR", status_code=400
        )


class InvalidDocument(AppException):
    def __init__(self):
        super().__init__(
            detail="Invalid Document", error_code="INVALID_DOCUMENT", status_code=400
        )


class PasswordNotMatch(AppException):
    def __init__(self):
        super().__init__(
            detail="The passwords do not match",
            error_code="PASSWORD_NOT_MATCH",
            status_code=400,
        )


class MatchingPasswords(AppException):
    def __init__(self):
        super().__init__(
            detail="The passwords cannot be the same",
            error_code="MACHING_PASSWORDS",
            status_code=400,
        )
