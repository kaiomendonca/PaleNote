class AppExceptionError(Exception):
    def __init__(self, detail: str, error_code: str, status_code: int):
        super().__init__(detail)
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code


# Backward-compatible alias for imports that still expect the old name
AppException = AppExceptionError
