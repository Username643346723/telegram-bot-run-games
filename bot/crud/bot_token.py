from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from bot.models.bot_token import BotToken
from sqlalchemy.exc import IntegrityError
from typing import Sequence
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


async def get_tokens_to_check(
        session: AsyncSession,
        check_type: str
) -> Sequence[BotToken]:
    """Получить токены для проверки по типу"""
    stmt = select(BotToken)

    if check_type == "inactive":
        stmt = stmt.where(BotToken.is_active == False)
    elif check_type == "recent":
        stmt = stmt.order_by(BotToken.created_at.desc()).limit(10)

    result = await session.execute(stmt)
    return result.scalars().all()


async def update_token_after_check(
        session: AsyncSession,
        token_id: int,
        is_active: bool,
        bot_id: int | None = None,
        bot_name: str | None = None,
        bot_username: str | None = None
) -> None:
    """Обновить токен после проверки"""
    await session.execute(
        update(BotToken)
        .where(BotToken.id == token_id)
        .values(
            is_active=is_active,
            bot_id=bot_id,
            bot_name=bot_name,
            bot_username=bot_username,
            last_check_at=func.now()
        )
    )


# Получение токена по строке
async def get_token_by_string(session: AsyncSession, token: str) -> BotToken | None:
    stmt = select(BotToken).where(BotToken.token == token)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


# Получение токена по ID
async def get_token_by_id(session: AsyncSession, token_id: int) -> BotToken | None:
    stmt = select(BotToken).where(BotToken.id == token_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


# Получение всех токенов пользователя
async def list_tokens_by_user(session: AsyncSession, user_id: int) -> Sequence[BotToken]:
    stmt = select(BotToken).where(BotToken.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().all()


# Создание нового токена
async def create_bot_token(
        session: AsyncSession,
        *,
        token: str,
        user_id: int,
        bot_id: int | None = None,
        bot_name: str | None = None,
        bot_username: str | None = None
) -> BotToken | None:
    new_token = BotToken(
        token=token,
        user_id=user_id,
        bot_id=bot_id,
        bot_name=bot_name,
        bot_username=bot_username,
        is_active=True,
    )
    session.add(new_token)
    try:
        await session.commit()
        await session.refresh(new_token)
        logger.info(f"✅ Bot token saved: {new_token.masked_token} for user {user_id}")
        return new_token
    except IntegrityError as e:
        await session.rollback()
        logger.warning(f"❌ Failed to save token (maybe duplicate): {token}. Error: {e}")
        return None
    except Exception as e:
        await session.rollback()
        logger.exception(f"❌ Unexpected error while saving token: {e}")
        return None


# Обновление информации о токене
async def update_bot_token_info(
        session: AsyncSession,
        token_id: int,
        *,
        bot_id: int | None = None,
        bot_name: str | None = None,
        bot_username: str | None = None,
        is_active: bool | None = None
) -> bool:
    stmt = (
        update(BotToken)
        .where(BotToken.id == token_id)
        .values(
            bot_id=bot_id,
            bot_name=bot_name,
            bot_username=bot_username,
            is_active=is_active,
        )
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount() > 0


# Бан токена
async def ban_token(session: AsyncSession, token_id: int, reason: str) -> bool:
    stmt = (
        update(BotToken)
        .where(BotToken.id == token_id)
        .values(is_banned=True, ban_reason=reason)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount() > 0


# Удаление токена (по id или токен-строке)
async def delete_token(session: AsyncSession, token_id: int) -> bool:
    stmt = delete(BotToken).where(BotToken.id == token_id)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount() > 0
