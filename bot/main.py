import asyncio
import sys
import traceback

from bot.client import bot, dp
from bot.handlers import router as router_main
from bot.utils import setup_logger

logger = setup_logger(__name__)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Необработанное исключение", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


async def main():
    try:
        logger.info('Старт программы')
        dp.include_router(router_main)
        await dp.start_polling(bot)

    except Exception as e:
        logger.critical("Необработанное исключение!", exc_info=True)

        # Альтернативно: подробный traceback вручную
        tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"Traceback:\n{tb_str}")

        # Можно завершить с кодом ошибки
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
