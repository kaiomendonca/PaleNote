class AppException(Exception):
    def __init__(self, detail: str, error_code: str, status_code: int):
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code
