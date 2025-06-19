import random
from pathlib import Path

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.config import settings
from bot.utils import setup_logger

logger = setup_logger(__name__)
router = Router()


async def get_random_username() -> str | None:
    """Получает случайный username из файла"""
    try:
        path = Path("resources/nicknames")
        if not path.exists():
            logger.error("Username file not found")
            return None

        with open(path, 'r') as file:
            usernames = [line.strip() for line in file if line.strip()]
            if not usernames:
                logger.warning("No usernames available in file")
                return None
            return random.choice(usernames)
    except Exception as e:
        logger.error(f"Error reading usernames file: {e}")
        return None


@router.callback_query(F.data == "generate_username")
async def handle_generate_username(callback: CallbackQuery):
    """Обработчик генерации username"""
    username = await get_random_username()

    if not username:
        await callback.message.answer(
            "❌ Все доступные имена ботов заняты.\n"
            "Пожалуйста, обратитесь к администратору для добавления новых вариантов."
        )

        # Логируем проблему для администратора
        logger.warning(
            f"User {callback.from_user.id} requested username but none available"
        )

        # Уведомление администраторам
        if settings.tg.admin_ids:
            for admin_id in settings.tg.admin_ids:
                await callback.bot.send_message(
                    admin_id,
                    f"⚠️ Закончились имена для ботов! Пользователь {callback.from_user.id} запросил имя."
                )
    else:
        await callback.message.answer(
            "🎲 <b>Сгенерирован username для бота:</b>\n\n"
            f"<code>@{username}</code>\n\n"
            "📌 <b>Как создать бота и получить токен:</b>\n"
            "1. Найти в Telegram <a href='https://t.me/BotFather'>@BotFather</a>\n"
            "2. Отправить команду <code>/newbot</code>\n"
            f"3. Ввести имя бота ({username})\n"
            f"4. Ввести username: <code>@{username}</code>\n"
            "5. Получить токен доступа\n\n"
            "🎥 <a href='https://www.youtube.com/shorts/miiZ_wSaA0g'>Видео-инструкция</a>\n\n"
            "🔑 <b>После создания отправь мне токен бота:</b>\n"
            "<i>Формат(Пример):</i> <code>1234567890:ABCdefGHIjklMnOpQRStuVWXYz</code>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    await callback.answer()
