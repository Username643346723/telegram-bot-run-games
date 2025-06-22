import uvicorn

from webhook_app.api import main_router
from webhook_app.core.client import app, bot
from webhook_app.core.config import settings

app.include_router(main_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    if settings.ENV == "development":
        await bot.set_webhook(url=f"{settings.WEBHOOK_BASE_URL}/webhook/{settings.tg.webhook_id_base_bot}")


if __name__ == '__main__':
    uvicorn.run(app, host=settings.gunicorn.host, port=settings.gunicorn.port)
