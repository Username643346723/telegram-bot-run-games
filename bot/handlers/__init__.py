from aiogram import Router
from .start import router as router_start
from .bot_token import router as router_token

router = Router()

router.include_router(router_start)
router.include_router(router_token)