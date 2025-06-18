import aiohttp
from aiogram import Router, F
from aiogram import types
from bot.utils import setup_logger

logger = setup_logger(__name__)
router = Router()


@router.message(F.text.regexp(r'^\d+:[A-Za-z\d_-]+$'))
async def process_token(message: types.Message):
    token = message.text.strip(' ').strip('\n')

    # Проверяем формат токена
    if not token.startswith("") or ":" not in token:
        await message.answer("Неверный формат токена. Пожалуйста, попробуй еще раз.")
        return

    is_valid, bot_info = await validate_token(token)

    if not is_valid:
        await message.answer("❌ Токен невалиден. Проверь и попробуй снова.")
        return

    # Сохраняем в базу
    # await save_bot_token_if_valid(token, message.from_user.id, bot_info)

    await message.answer(
        f"✅ Токен принят. Бот: {bot_info.get('username')}.\n"
        "Теперь он будет использоваться в системе."
    )


async def validate_token(token: str) -> tuple[bool, dict]:
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{token}/getMe"
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("ok"):
                        return True, data.get("result")
        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
    return False, {}
