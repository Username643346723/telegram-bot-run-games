from typing import Sequence

from sqlalchemy import select, func, String
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.users import User
from bot.models.bot_token import BotToken



async def get_recent_users(session: AsyncSession, limit: int = 10) -> Sequence[User]:
    """Получить последних пользователей с количеством их токенов"""
    stmt = (
        select(User)
        .order_by(User.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_user_with_tokens_count(session: AsyncSession, user_id: int) -> tuple[User, int]:
    """Получить пользователя с количеством его токенов"""
    user = await get_user_by_id(session, user_id)
    if not user:
        return None, 0

    tokens_count = await session.scalar(
        select(func.count(BotToken.id))
        .where(BotToken.user_id == user_id)
    )
    return user, tokens_count


async def search_users(session: AsyncSession, search_query: str) -> Sequence[User]:
    """Поиск пользователей по ID или username"""
    stmt = select(User).where(
        (User.username.ilike(f"%{search_query}%")) |
        (User.id.cast(String).ilike(f"%{search_query}%")) |
        (User.full_name.ilike(f"%{search_query}%"))
    ).order_by(User.created_at.desc()).limit(20)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    stmt = select(User).where(User.id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_or_update_user(session: AsyncSession, *, user_id: int, full_name: str | None = None,
                                username: str | None = None, language_code: str | None = None) -> User:
    user = await get_user_by_id(session, user_id)

    if user is None:
        user = User(id=user_id)
        session.add(user)

    user.full_name = full_name
    user.username = username
    user.language_code = language_code

    await session.commit()
    await session.refresh(user)
    return user
