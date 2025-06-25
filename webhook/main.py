from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI

from bot.handlers import router_main
from bot.handlers.bot_game import user_bots_router
from core.bot import main_bot, main_bot_dp, user_bots_dp
from core.config import settings
from libs.logging.logger import setup_logger
from webhook.api import main_router

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Контекст жизненного цикла приложения с обработкой webhook"""

    if settings.ENV == "development":
        assert settings.WEBHOOK_BASE_URL.startswith("https"), "В продакшне обязателен HTTPS!"

        webhook_url = f"{settings.WEBHOOK_BASE_URL}/api/v1/webhook/{settings.tg.webhook_id_base_bot}"
        logger.info(f"Setting webhook: {webhook_url}")
        await main_bot.set_webhook(url=webhook_url)
    yield
    # Добавьте при необходимости логику cleanup
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan  # Явное указание lifespan
)
app.include_router(main_router, prefix="/api/v1")

main_bot_dp.include_router(router_main)
user_bots_dp.include_router(user_bots_router)

logger.info(
    f"Starting app in {settings.ENV} mode\n"
    f"Docs: http://{settings.gunicorn.host}:{settings.gunicorn.port}/docs"
)

if __name__ == '__main__':
    uvicorn.run(app, host=settings.gunicorn.host, port=settings.gunicorn.port)
