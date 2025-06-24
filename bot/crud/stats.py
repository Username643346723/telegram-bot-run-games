from datetime import datetime, timedelta, UTC

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.bot_token import BotToken
from bot.models.users import User


async def get_system_stats(session: AsyncSession) -> dict:
    """Получение системной статистики"""
    stats = dict()

    # Статистика по пользователям
    stats['users'] = await session.scalar(select(func.count(User.id)))

    # Статистика по токенам
    total_tokens = await session.scalar(select(func.count(BotToken.id))) or 0
    active_tokens = await session.scalar(
        select(func.count(BotToken.id)).where(BotToken.is_active.is_(True))
    ) or 0

    stats['tokens'] = total_tokens
    stats['active_tokens'] = active_tokens
    stats['inactive_tokens'] = total_tokens - active_tokens

    # Заблокированные токены
    stats['banned_tokens'] = await session.scalar(
        select(func.count(BotToken.id)).where(BotToken.is_banned.is_(True))
    ) or 0

    # Новые пользователи за последнюю неделю
    last_week = datetime.now(UTC) - timedelta(days=7)
    stats['last_week_users'] = await session.scalar(
        select(func.count(User.id)).where(User.created_at >= last_week)
    ) or 0

    return stats
