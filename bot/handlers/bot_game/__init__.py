from aiogram import Router
from .start import router as router_start


# Общий роутер для всех пользовательских ботов
user_bots_router = Router()

user_bots_router.include_router(router_start)
