from fastapi import FastAPI

from webhook_app.core.config import settings
from webhook_app.utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# Логируем информацию о запуске приложения

logger.info("Application has started")

