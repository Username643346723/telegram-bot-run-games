from aiogram import Router
from aiogram import types
from aiogram.filters.command import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.crud.user import create_or_update_user
from core.db.session import db_helper
from libs.logging import setup_logger

logger = setup_logger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    logger.info(
        "User %s (%s) started bot. Username: @%s, language: %s",
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username or "no_username",
        message.from_user.language_code or "unknown"
    )

    async with db_helper.session_factory() as session:
        await create_or_update_user(
            session,
            user_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
            language_code=message.from_user.language_code,
        )

    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Сгенерировать username", callback_data="generate_username")

    await message.answer(
        "👋 <b>Привет, создатель ботов!</b>\n\n"
        "✨ <i>Давай сделаем твоего бота популярнее вместе!</i>\n\n"
        "🎮 <b>Как это работает:</b>\n"
        "▫️ Ты делишься со мной токеном своего бота\n"
        "▫️ Я добавляю в него 10 увлекательных игр\n"
        "▫️ Твои подписчики получают крутые развлечения\n"
        "▫️ Ты привлекаешь больше аудитории\n\n"
        "🤝 <b>Это взаимовыгодно:</b>\n"
        "• Твой бот становится интереснее\n"
        "• Я знакомлю людей с играми\n"
        "• Все получают классный игровой опыт!\n\n"
        "🔑 <b>Просто отправь мне токен бота</b>\n"
        "<i>Или давай создадим нового — жми кнопку ниже:</i>",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )
