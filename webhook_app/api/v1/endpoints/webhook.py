from fastapi import APIRouter, Request, HTTPException
from webhook_app.core.config import settings
from webhook_app.services.webhook_handler import handle_telegram_update

router = APIRouter()


@router.post("/webhook/{bot_id}")
async def telegram_webhook(
        bot_id: str,
        request: Request,
        secret: str
):
    if secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    data = await request.json()
    await handle_telegram_update(bot_id=bot_id, update_data=data)
    return {"ok": True}
