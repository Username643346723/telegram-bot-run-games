from aiogram import Router, F
from aiogram import types
from aiogram.filters.command import CommandStart


router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Отправь мне токен бота для проверки.\n"
        "Используй команду /add_token"
    )
