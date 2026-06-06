from sqlalchemy.orm import DeclarativeBase

from app.database.session import engine


class Base(DeclarativeBase):
    pass


def init_db():
    Base.metadata.create_all(bind=engine)
