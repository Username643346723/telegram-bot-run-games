from aiogram import Router
from .start import router as router_start
from .bot_token import router as router_token
from .admin.admin import router as router_admin
from .bot_username import router as router_username

router_main = Router()

router_main.include_router(router_start)
router_main.include_router(router_token)
router_main.include_router(router_admin)
router_main.include_router(router_username)