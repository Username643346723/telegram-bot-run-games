from aiogram.exceptions import TelegramNetworkError
from fastapi import Request

from bot.crud.bot_token import get_token_by_webhook_id
from core.bot import user_bots_dp, main_bot, main_bot_dp
from core.db.session import db_helper
from libs.logging.logger import setup_logger
from utils import token

logger = setup_logger(__name__)


async def handle_telegram_update_base_bot(
        webhook_id: str,
        request_json_data: dict,
):
    await main_bot_dp.feed_webhook_update(main_bot, request_json_data)


async def handle_telegram_update_other_bot(
        webhook_id: str,
        request_json_data: dict,
        request: Request

):
    async with db_helper.session_factory() as session:
        bot_token = await get_token_by_webhook_id(session, webhook_id=webhook_id)
        if bot_token is None:
            logger.warning(
                "Invalid webhook request",
                extra={
                    "webhook_id": webhook_id,
                    "ip": request.client.host,
                    "user_agent": request.headers.get("user-agent")
                }
            )
            return

    _bot = token.get_user_bot(bot_token.token)
    try:
        await user_bots_dp.feed_webhook_update(_bot, request_json_data)
    except TelegramNetworkError as e:
        logger.error(f"Telegram API error for bot {webhook_id}: {e}")
