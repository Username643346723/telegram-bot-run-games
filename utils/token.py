from typing import Sequence

import aiohttp
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.handlers.bot_token import logger
from bot.models import BotToken
from core.bot import active_user_bots
from bot.crud.bot_token import get_tokens_to_check
from core.config import settings
from core.db.session import db_helper


async def validate_token(token: str) -> tuple[bool, dict]:
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("ok") and data.get("result"):
                        return True, data["result"]
                else:
                    logger.warning(f"Telegram API responded with status {response.status} for token: {token}")
    except Exception as e:
        logger.warning(f"Exception during token validation: {e}")
    return False, {}


async def get_user_bot(token: str) -> Bot:
    if token not in active_user_bots:
        active_user_bots[token] = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    return active_user_bots[token]


# При удалении бота чистим кэш
async def remove_user_bot(token: str):
    if token in active_user_bots:
        bot = active_user_bots.pop(token)
        await bot.session.close()


async def init_user_bots(tokens: Sequence[BotToken] | None = None) -> None:
    """Инициализация пользовательских ботов и установка webhook'ов"""
    if tokens is None:
        async with db_helper.session_factory() as session:
            tokens = await get_tokens_to_check(session, check_type="recent", limit=10000)

    initialized = 0

    for token in tokens:
        if token.token not in active_user_bots:
            bot = Bot(token=token.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
            active_user_bots[token.token] = bot

            webhook_url = f"{settings.WEBHOOK_BASE_URL}/api/v1/other_bot/webhook/{token.webhook_id}"
            await bot.set_webhook(url=webhook_url)

            logger.info(f"[+] Webhook установлен для бота: {token.token}")
            initialized += 1

    logger.info(f"Инициализировано {initialized} новых ботов из {len(tokens)}")