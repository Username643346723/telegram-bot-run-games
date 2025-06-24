from aiogram import Dispatcher
from core.bot import bot, dp  # Импорт из core/bot.py
from core.config import settings
from libs.logging import setup_logger
from bot.handlers import router_main  # Локальный импорт

logger = setup_logger(__name__)


async def main():
    dp.include_router(router_main)

    logger.info(
        f"Starting bot in polling mode...\n"
        f"Environment: {settings.ENV}\n"
        f"Bot ID: {bot.id}"
    )

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Bot crashed: {e}")
        raise
    finally:
        logger.info("Bot stopped")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())