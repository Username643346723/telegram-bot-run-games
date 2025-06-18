from aiogram import Router, F
from aiogram import types
from aiogram.filters.command import CommandStart
from bot.utils import setup_logger

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
    await message.answer(
        "Привет! Отправь мне токен бота для проверки.\n"
        "Используй команду /add_token"
    )
