from aiogram import Router
from core.config import settings
from libs.logging.logger import setup_logger

logger = setup_logger(__name__)

router = Router()


@router.message(lambda msg: msg.text == "/start")
async def handle_start(msg):
    await msg.answer("Бот запущен!")


async def handle_telegram_update(bot_id: str, update_data: dict):
    if settings.tg.webhook_id_base_bot == bot_id:
        logger.info(str(update_data))
