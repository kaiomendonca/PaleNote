from app.core.app_exception import AppExceptionError


class UserCreationError(AppExceptionError):
    def __init__(self):
        super().__init__(
            detail="User cannot be created",
            error_code="USER_NOT_CREATED",
            status_code=500,
        )


class UploadFailedError(AppExceptionError):
    def __init__(self):
        super().__init__(
            detail="Upload failed", error_code="UPLOAD_FAILED", status_code=500
        )


class UserInvalidError(AppExceptionError):
    def __init__(self):
        super().__init__(
            detail="Invalid user", error_code="USER_INVALID_ERROR", status_code=400
        )


class InvalidDocumentError(AppExceptionError):
    def __init__(self):
        super().__init__(
            detail="Invalid Document", error_code="INVALID_DOCUMENT", status_code=400
        )


class PasswordNotMatchError(AppExceptionError):
    def __init__(self):
        super().__init__(
            detail="The passwords do not match",
            error_code="PASSWORD_NOT_MATCH",
            status_code=400,
        )


class MatchingPasswordsError(AppExceptionError):
    def __init__(self):
        super().__init__(
            detail="The passwords cannot be the same",
            error_code="MACHING_PASSWORDS",
            status_code=400,
        )


class EmailAlreadyExistsError(AppExceptionError):
    def __init__(self):
        super().__init__(
            detail="Email Already Exists",
            error_code="EMAIL_ALREADY_EXISTS",
            status_code=400,
        )
