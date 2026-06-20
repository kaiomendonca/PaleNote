from sqlalchemy.orm import DeclarativeBase

from app.database.session import engine


class Base(DeclarativeBase):
    pass


async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
