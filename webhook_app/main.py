import uvicorn

from webhook_app.api import main_router
from core.client import app, bot, dp
from core.config import settings
from bot.handlers import router

from utils.logger import setup_logger

logger = setup_logger(__name__)

app.include_router(main_router, prefix="/api/v1")
dp.include_router(router)


@app.on_event("startup")
async def startup():
    if settings.ENV == "development":
        url = f"{settings.WEBHOOK_BASE_URL}/webhook/{settings.tg.webhook_id_base_bot}"
        logger.info(f"Set webhook url: {url}")
        await bot.set_webhook(url=f"{settings.WEBHOOK_BASE_URL}/api/v1/webhook/{settings.tg.webhook_id_base_bot}")


if __name__ == '__main__':
    uvicorn.run(app, host=settings.gunicorn.host, port=settings.gunicorn.port)
