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
        query = select(Users).where(Users.document == document)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def get_by_email(self, email: str) -> Users:
        query = select(Users).where(Users.email == email)
        result = await self.db.execute(query)
        user_by_email = result.scalar_one_or_none()
        return user_by_email

    async def update_password(self, user_id: str, password: str) -> None:
        query = select(Users).where(Users.id_ == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        user.password_hash = password

    async def exists_by_email(self, email: str) -> bool:
        query = select(exists().where(Users.email == email))
        result = await self.db.execute(query)

        return result.scalar()

    async def exists_by_document(self, document: str) -> bool:
        query = select(exists().where(Users.document == document))
        result = await self.db.execute(query)

        return result.scalar()
