from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_current_active_user
from app.models.users import Users
from app.schemas.users import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Return the current authenticated user profile",
)
async def get_me(
    user: Annotated[Users, Depends(get_current_active_user)],
) -> UserResponse:
    return UserResponse.model_validate(user)
