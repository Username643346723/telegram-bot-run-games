from sqlalchemy import Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB  # если используется PostgreSQL

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

    title: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="Название игры"
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

    site_url: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        comment="Ссылка на сайт с информацией об игре"
    )

    play_url: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        comment="Ссылка на игру (для запуска)"
    )

    category: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="Категория игры (например, стратегия, аркада и т.д.)"
    )

    rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Рейтинг игры (от 0 до 5, например)"
    )

    tags: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Список тегов, связанных с игрой"
    )

    def __repr__(self) -> str:
        return f"Game(id={self.id}, game_id={self.game_id}, title={self.title})"
