from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.models.users import User


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
