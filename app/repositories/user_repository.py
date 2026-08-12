from typing import Any

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import Users


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: Users) -> Users:
        self.db.add(user_data)
        await self.db.flush()
        return user_data

    async def get_by_document(self, document: str) -> Users | None:
        query = select(Users).where(
            Users.document == document,
            Users.is_active.is_(True),
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def get_by_email(self, email: str) -> Users | None:
        query = select(Users).where(
            Users.email == email,
            Users.is_active.is_(True),
        )
        result = await self.db.execute(query)
        user_by_email = result.scalar_one_or_none()
        return user_by_email

    async def list_all(self) -> list[Users]:
        query = select(Users).where(Users.is_active.is_(True))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_password(self, user: Users, password_hash: str) -> None:
        user.password_hash = password_hash

    async def update_user(self, user: Users, fields: dict[str, Any]) -> Users:
        for key, value in fields.items():
            setattr(user, key, value)
        return user

    async def delete_user(self, user: Users) -> None:
        user.is_active = False

    async def exists_by_email(self, email: str) -> bool:
        query = select(exists().where(Users.email == email))
        result = await self.db.execute(query)

        return result.scalar()

    async def exists_by_document(self, document: str) -> bool:
        query = select(exists().where(Users.document == document))
        result = await self.db.execute(query)

        return result.scalar()
