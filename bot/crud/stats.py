from sqlalchemy import func, select
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.bot_token import BotToken
from bot.models.users import User


async def get_system_stats(session: AsyncSession) -> dict:
    """Получение системной статистики"""
    stats = {}

    # Статистика по пользователям
    users_count = await session.scalar(select(func.count(User.id)))
    stats['users'] = users_count

    # Статистика по токенам
    total_tokens = await session.scalar(select(func.count(BotToken.id)))
    active_tokens = await session.scalar(
        select(func.count(BotToken.id))
        .where(BotToken.is_active == True)
    )

    stats['tokens'] = total_tokens
    stats['active_tokens'] = active_tokens
    stats['inactive_tokens'] = total_tokens - active_tokens if total_tokens else 0

    # Дополнительная статистика
    stats['banned_tokens'] = await session.scalar(
        select(func.count(BotToken.id))
        .where(BotToken.is_banned == True)
    )

    # Для SQLite используем datetime() и модификаторы даты
    stats['last_week_users'] = await session.scalar(
        select(func.count(User.id))
        .where(User.created_at >= text("datetime('now', '-7 days')"))
    )

    return stats
