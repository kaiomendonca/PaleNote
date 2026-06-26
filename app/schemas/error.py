from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str = Field(description="Descriptive error message")
    error_code: str | None = Field(
        default=None, description="Internal error code for tracking"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Moment the error occurred",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "User not found",
                "error_code": "USER_NOT_FOUND",
                "timestamp": "2026-05-09T15:30:00Z",
            }
        }
    }
