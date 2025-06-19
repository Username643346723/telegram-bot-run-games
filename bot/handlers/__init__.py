from aiogram import Router
from .start import router as router_start
from .bot_token import router as router_token
from .admin import router as router_admin
from .bot_username import router as router_username

router = Router()

router.include_router(router_start)
router.include_router(router_token)
router.include_router(router_admin)
router.include_router(router_username)