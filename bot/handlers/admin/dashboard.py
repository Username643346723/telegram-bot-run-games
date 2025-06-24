# Статистика
from aiogram import Router, F
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.views.keyboards.admin import admin_main_kb, AdminCallback, AdminAction
from bot.crud.bot_token import *
from bot.crud.stats import get_system_stats
from core.db.session import db_helper
from libs.logging import setup_logger

logger = setup_logger(__name__)
router = Router()


@router.callback_query(AdminCallback.filter(F.action == AdminAction.stats))
async def handle_stats(callback: types.CallbackQuery):
    async with db_helper.session_factory() as session:
        stats = await get_system_stats(session)

        text = (
            "📊 <b>Системная статистика</b>\n\n"
            "👥 <b>Пользователи:</b>\n"
            f"• Всего: {stats['users']}\n"
            f"• Новых за неделю: {stats['last_week_users']}\n\n"
            "🤖 <b>Токены ботов:</b>\n"
            f"• Всего: {stats['tokens']}\n"
            f"• Активных: {stats['active_tokens']}\n"
            f"• Неактивных: {stats['inactive_tokens']}\n"
            f"• Заблокированных: {stats['banned_tokens']}"
        )

        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Обновить", callback_data="admin:stats")
        builder.button(text="◀️ Назад", callback_data="admin:back")
        builder.adjust(2)

        try:
            await callback.message.edit_text(
                text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error editing stats message: {e}")
            await callback.answer("Ошибка обновления статистики")

        await callback.answer()
