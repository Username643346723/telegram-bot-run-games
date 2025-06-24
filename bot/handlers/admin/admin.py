# bot/handlers/admin.py
from aiogram import Router, F
from core.config import settings

from .menu import router as router_menu
from .users import router as router_user
from .tokens import router as router_token
from .dashboard import router as router_dashboard
from .games import router as router_game

router = Router()
router.message.filter(F.from_user.id.in_(settings.tg.admins_id))

router.include_router(router_menu)
router.include_router(router_user)
router.include_router(router_token)
router.include_router(router_dashboard)
router.include_router(router_game)
