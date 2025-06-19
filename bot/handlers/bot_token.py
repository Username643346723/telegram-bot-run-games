from aiogram import Router, F
from aiogram import types

from bot.crud.bot_token import *
from bot.crud.user import get_user_by_telegram_id, create_or_update_user
from bot.models import db_helper
from bot.utils.token import validate_token

logger = setup_logger(__name__)
router = Router()


@router.message(F.text.regexp(r'^\d+:[A-Za-z\d_-]+$'))
async def process_token(message: types.Message):
    token = message.text.strip()

    if ":" not in token:
        logger.info(f"Invalid token format from user {message.from_user.id}: {token}")
        return await message.answer("❌ Неверный формат токена. Попробуй снова.")

    is_valid, bot_info = await validate_token(token)
    if not is_valid:
        logger.info(f"Token validation failed for user {message.from_user.id}: {token}")
        return await message.answer("❌ Токен невалиден. Проверь и попробуй снова.")

    logger.info(f"Valid token received from user {message.from_user.id}: {bot_info}")

    async with db_helper.session_factory() as session:
        existing_token = await get_token_by_string(session, token=token)
        if existing_token:
            logger.info(f"Duplicate token from user {message.from_user.id}: {token}")
            return await message.answer("⚠️ Такой токен уже существует в системе.")

        user = await get_user_by_telegram_id(session, telegram_id=message.from_user.id)
        if not user:
            user = await create_or_update_user(
                session=session,
                user_id=message.from_user.id,
                full_name=message.from_user.full_name,
                username=message.from_user.username,
                language_code=message.from_user.language_code,
            )
            logger.info(f"Created new user record for {message.from_user.id}")

        await create_bot_token(
            session=session,
            token=token,
            user_id=user.id,
            bot_name=bot_info.get("first_name", ""),
            bot_username=bot_info.get("username", "")
        )
        logger.info(f"Token saved for bot @{bot_info.get('username')} by user {message.from_user.id}")

    await message.answer(
        f"🎉  <b>Токен принят!</b>\n"
        f"🤖  @{bot_info.get('username', 'неизвестно')}\n"
        f"📥  Успешно добавлен в обработку\n\n"
        "🛠   <i>Что сейчас происходит:</i>\n"
        "├─ 🎮 Добавление 10 игр\n"
        "└─ 🔧 Техническая проверка\n\n"
        "⏳   <b>Обычно занимает:</b>\n"
        "└─  Около 1 часа\n\n"
        "💡 Проверь через час командой /start\n"
        "🌸 Спасибо за доверие!",
        parse_mode="HTML"
    )
