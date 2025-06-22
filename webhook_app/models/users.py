from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .bot_token import BotToken


class User(Base):
    __tablename__ = "users"
    __table_args__ = {
        'comment': 'Пользователи, которые взаимодействовали с ботом'
    }

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=False,
        comment="Telegram user ID"
    )
    full_name: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="Полное имя пользователя"
    )
    username: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="Username пользователя (@ без @)"
    )
    language_code: Mapped[str | None] = mapped_column(
        String(8),
        nullable=True,
        comment="Код языка пользователя"
    )
    is_blocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default='false',
        comment="Заблокировал ли пользователь бота"
    )

    # связь с токенами
    tokens: Mapped[list["BotToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, username=@{self.username})"
