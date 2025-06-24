from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI

from core.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

bot = Bot(
    token=settings.tg.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# Логируем информацию о запуске приложения

logger.info("Application has started")
