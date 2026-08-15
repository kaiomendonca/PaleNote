from app.core.security import hash_password, verify_password
from app.core.user_exceptions import (
    EmailAlreadyExistsError,
    InvalidDocumentError,
    UserNotFoundError,
)
from app.models.users import Users
from app.repositories.user_repository import UserRepository
from app.schemas.users import (
    ChangePassword,
    PersonType,
    UserCreate,
    UserResponse,
    UserUpdate,
)


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
            **{
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

        verify_password(payload.current_password, user.password_hash)

        new_hash = hash_password(payload.new_password)
        await self.repository.update_password(user, new_hash)

    async def get_user(self, document: str) -> UserResponse:
        user = await self.repository.get_by_document(document)
        if not user:
            raise UserNotFoundError()
        return UserResponse.model_validate(user)

    async def list_users(self) -> list[UserResponse]:
        users = await self.repository.list_all()
        return [UserResponse.model_validate(user) for user in users]

    async def update_user(self, document: str, payload: UserUpdate) -> UserResponse:
        user = await self.repository.get_by_document(document)
        if not user:
            raise UserNotFoundError()

        if payload.email and payload.email != user.email:
            if await self.repository.exists_by_email(payload.email):
                raise EmailAlreadyExistsError()

        if payload.document and payload.document != user.document:
            if await self.repository.exists_by_document(payload.document):
                raise InvalidDocumentError()

        fields = payload.model_dump(exclude_unset=True, exclude_none=True)
        updated_user = await self.repository.update_user(user, fields)

        return UserResponse.model_validate(updated_user)

    async def delete_user(self, document: str) -> None:
        user = await self.repository.get_by_document(document)
        if not user:
            raise UserNotFoundError()
        await self.repository.delete_user(user)
