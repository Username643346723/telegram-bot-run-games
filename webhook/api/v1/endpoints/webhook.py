from aiogram.types import Update
from fastapi import APIRouter, Request

from core.bot import dp
from libs.logging.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


@router.post("/webhook/{webhook_id}")
async def telegram_webhook(
        webhook_id: str,
        request: Request,
):
    logger.info(f"webhook_id: {webhook_id}, request: {str(request)}")
    body = await request.body()
    logger.info(f"Raw body: {body}")
    # if secret != settings.WEBHOOK_SECRET:
    #     raise HTTPException(status_code=403, detail="Forbidden")

    json_data = await request.json()
    update = Update(**json_data)

    await dp.process_update(update)

    # await handle_telegram_update(bot_id=webhook_id, update_data=data)
    return {"ok": True}
