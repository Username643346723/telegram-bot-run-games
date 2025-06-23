from fastapi import APIRouter, Request, HTTPException

from webhook_app.core.config import settings
from webhook_app.services.webhook_handler import handle_telegram_update
from webhook_app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


@router.post("/webhook/{webhook_id}")
async def telegram_webhook(
        webhook_id: str,
        request: Request,
        secret: str
):
    logger.info(f"webhook_id: {webhook_id}, request: {str(request)}")
    if secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    data = await request.json()
    await handle_telegram_update(bot_id=webhook_id, update_data=data)
    return {"ok": True}
