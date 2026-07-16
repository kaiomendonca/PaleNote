import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PersonType(str, Enum):
    INDIVIDUAL = "individual"
    COMPANY = "company"


class Users(Base):
    __tablename__ = "users"

    id_: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    person_type: Mapped[PersonType] = mapped_column(
        SQLEnum(PersonType),
        nullable=False,
    )

    document: Mapped[str] = mapped_column(String(14), index=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
