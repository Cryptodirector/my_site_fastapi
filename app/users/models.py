from sqlalchemy import String, Float
from sqlalchemy.orm import mapped_column, Mapped

from app.database.config import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(), nullable=False)
    api_key: Mapped[str] = mapped_column(String(), nullable=False)
    api_secret: Mapped[str] = mapped_column(String(), nullable=False)
    balance: Mapped[float] = mapped_column(Float(), nullable=True, default=0)
