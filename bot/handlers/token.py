from aiogram import Router, F
from aiogram import types
from bot.utils import setup_logger

logger = setup_logger(__name__)
router = Router()


@router.message(F.text.regexp(r'\d+:[A-Za-z\d-]+'))
async def process_token(message: types.Message):
    token = message.text.strip(' ').strip('\n')

    # Проверяем формат токена
    if not token.startswith("") or ":" not in token:
        await message.answer("Неверный формат токена. Пожалуйста, попробуй еще раз.")
        return

    # todo продолжить здесь