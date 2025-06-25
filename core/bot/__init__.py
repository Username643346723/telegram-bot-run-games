from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config.app import settings

main_bot = Bot(
    token=settings.tg.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

main_bot_dp = Dispatcher()  # Основной диспетчер, который отвечает работу основного бота

user_bots_dp = Dispatcher()  # Диспетчер отвечающий за ботов добавленных пользователями

active_user_bots: dict[str, Bot] = {}
