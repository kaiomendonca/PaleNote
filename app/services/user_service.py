from app.core.security import hash_password, verify_password
from app.core.user_exceptions import (
    EmailAlreadyExistsError,
    InvalidDocumentError,
    PasswordNotMatchError,
    UserNotFoundError,
)
from app.models.users import Users
from app.repositories.user_repository import UserRepository
from app.schemas.users import ChangePassword, PersonType, UserCreate, UserResponse


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, payload: UserCreate) -> UserResponse:
        if await self.repository.exists_by_email(payload.email):
            raise EmailAlreadyExistsError()

        if await self.repository.exists_by_document(payload.document):
            raise InvalidDocumentError()

        person_type = (
            PersonType.INDIVIDUAL if len(payload.document) == 11 else PersonType.COMPANY
        )

        hashed_password = hash_password(payload.password)

        user = Users(
            {
                **payload.model_dump(exclude={"password"}),
                "password_hash": hashed_password,
                "person_type": person_type,
            }
        )

        created_user = await self.repository.create_user(user)

        return UserResponse.model_validate(created_user)

    async def change_password(self, document: str, payload: ChangePassword) -> None:
        user = await self.repository.get_by_document(document)
        if not user:
            raise UserNotFoundError()

        if not verify_password(
            payload.current_password,
            user.password_hash,
        ):
            raise PasswordNotMatchError()

        new_hash = hash_password(payload.new_password)
        await self.repository.update_password(user, new_hash)
