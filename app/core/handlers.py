from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.app_exception import AppException
from app.schemas.error import ErrorResponse


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.detail, error_code=exc.error_code).model_dump(
            mode="json"
        ),
    )
