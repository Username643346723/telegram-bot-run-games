from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.db.models import Base


class Game(Base):
    __tablename__ = "games"
    __table_args__ = {
        'comment': 'Таблица доступных игр для Telegram-бота'
    }

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный внутренний идентификатор игры"
    )

    game_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True,
        comment="ID игры (внешний или с платформы)"
    )

    image: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        comment="URL изображения обложки игры"
    )

    descriptions: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="HTML-описание игры для отображения в боте"
    )

    def __repr__(self) -> str:
        return f"Game(id={self.id}, game_id={self.game_id})"
