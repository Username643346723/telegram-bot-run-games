from fastapi import APIRouter, Request

from core.config import settings
from libs.logging.logger import setup_logger
from webhook.services.webhook_handler import (
    handle_telegram_update_base_bot,
    handle_telegram_update_other_bot
)

logger = setup_logger(__name__)
router = APIRouter()


@router.post("/webhook/{webhook_id}")
async def telegram_webhook_base_bot(
        webhook_id: str,
        request: Request,
):
    if settings.tg.webhook_id_base_bot != webhook_id:
        body = await request.body()

        logger.error(f"Webhook_id основного бота, "
                     f"который был передан телеграмм не "
                     f"соответствует установленному в настройках. "
                     f"Webhook_id: {webhook_id}, Request body: {str(body)}")
        return {"ok": True}

    json_data = await request.json()

    await handle_telegram_update_base_bot(webhook_id, request_json_data=json_data)

    return {"ok": True}


@router.post("/other_bot/webhook/{webhook_id}")
async def telegram_webhook_other_bot(
        webhook_id: str,
        request: Request,
):
    json_data = await request.json()

    await handle_telegram_update_other_bot(webhook_id, request_json_data=json_data)

    return {"ok": True}
