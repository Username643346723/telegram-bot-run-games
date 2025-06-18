from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String, Boolean, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .users import User

if TYPE_CHECKING:
    from .users import User


class BotToken(Base):
    __tablename__ = "bot_tokens"
    __table_args__ = {
        'comment': 'Таблица для хранения токенов телеграм ботов и их статусов'
    }

    # Основные поля
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор записи"
    )

    bot_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        comment="ID бота, полученный из getMe"
    )

    token: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        comment="Токен бота Telegram (частично скрывается при выводе)"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default='false',
        comment="Флаг активности токена (прошел ли проверку)"
    )
    bot_name: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="Название бота, полученное из getMe"
    )
    bot_username: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="Юзернейм бота (без @)"
    )

    # Мета-поля
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Дата и время добавления токена"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Дата и время последнего обновления записи"
    )
    last_check_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата и время последней проверки токена"
    )
    check_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default='0',
        comment="Количество проведенных проверок токена"
    )

    # Дополнительные поля для администрирования
    is_banned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default='false',
        comment="Флаг бана токена (недействителен)"
    )
    ban_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Причина бана токена"
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID пользователя, который добавил токен"
    )

    user: Mapped["User"] = relationship(
        back_populates="tokens"
    )

    def __repr__(self) -> str:
        return (
            f"BotToken(id={self.id}, "
            f"bot='{self.bot_name}', "
            f"username=@{self.bot_username}, "
            f"active={self.is_active})"
        )

    @property
    def masked_token(self) -> str:
        """Возвращает частично скрытый токен для безопасного отображения"""
        if len(self.token) < 10:
            return "***"
        visible_part = self.token[:4]
        hidden_part = '*' * (len(self.token) - 8)
        last_part = self.token[-4:]
        return f"{visible_part}{hidden_part}{last_part}"
