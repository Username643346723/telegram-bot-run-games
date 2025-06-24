# Поиск / просмотр пользователей
from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.crud.bot_token import *
from bot.crud.user import get_recent_users, search_users
from bot.views.keyboards.admin import AdminAction, AdminCallback
from core.db.session import db_helper
from libs.logging import setup_logger

logger = setup_logger(__name__)
router = Router()


class UserSearch(StatesGroup):
    waiting_for_query = State()
    showing_results = State()


@router.callback_query(AdminCallback.filter(F.action == AdminAction.users_list))
async def handle_users_list(callback: types.CallbackQuery):
    async with db_helper.session_factory() as session:
        # Получаем данные через CRUD методы
        users = await get_recent_users(session)

        if not users:
            await callback.message.edit_text("Нет пользователей")
            return

        builder = InlineKeyboardBuilder()
        user_lines = []

        for user in users:
            # Получаем токены пользователя
            tokens = await list_tokens_by_user(session, user.id)
            tokens_count = len(tokens)

            # Формируем информацию о токенах
            token_info = ""
            if tokens:
                # Берем первый токен (можно изменить логику для отображения всех)
                token = tokens[0].token
                masked_token = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "****"
                token_info = f" | 🔑 {masked_token}"
                if tokens_count > 1:
                    token_info += f" (+{tokens_count - 1})"

            user_info = (
                f"{user.full_name or 'Без имени'}"
                f" (@{user.username})" if user.username else ""
            )

            builder.button(
                text=f"{user_info} | 🗝️ {tokens_count} ток.",
                callback_data=f"admin:user_detail:{user.id}"
            )
            user_lines.append(
                f"{len(user_lines) + 1}. {user_info}"
                f" | 🗝️ {tokens_count} ток."
                f"{token_info}"
            )

        builder.button(text="◀️ Назад", callback_data="admin:back")
        builder.adjust(1)

        await callback.message.edit_text(
            "Последние пользователи:\n\n" + "\n".join(user_lines),
            reply_markup=builder.as_markup()
        )


@router.callback_query(AdminCallback.filter(F.action == AdminAction.user_search))
async def start_user_search(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите ID, username или имя пользователя:",
        reply_markup=InlineKeyboardBuilder()
        .button(text="◀️ Назад", callback_data="admin:back")
        .as_markup()
    )
    await state.set_state(UserSearch.waiting_for_query)
    await callback.answer()


@router.message(UserSearch.waiting_for_query)
async def process_search_query(message: types.Message, state: FSMContext):
    search_query = message.text.strip()

    async with db_helper.session_factory() as session:
        users = await search_users(session, search_query)

        if not users:
            await message.answer("Пользователи не найдены")
            await state.clear()
            return

        builder = InlineKeyboardBuilder()
        user_lines = []

        for user in users:
            # Получаем токены пользователя
            tokens = await list_tokens_by_user(session, user.id)
            tokens_count = len(tokens)

            # Формируем информацию о токенах
            token_info = ""
            if tokens:
                # Берем первый токен (можно изменить логику для отображения всех)
                token = tokens[0].token
                masked_token = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "****"
                token_info = f" | 🔑 {masked_token}"
                if tokens_count > 1:
                    token_info += f" (+{tokens_count - 1})"

            user_info = f"{user.full_name or 'Без имени'}"
            if user.username:
                user_info += f" (@{user.username})"

            builder.button(
                text=f"{user_info} | 🗝️ {tokens_count} ток.",
                callback_data=f"admin:user_detail:{user.id}"
            )
            user_lines.append(
                f"{len(user_lines) + 1}. {user_info}"
                f" | 🗝️ {tokens_count} ток."
                f"{token_info}"
            )

        builder.button(text="◀️ Назад", callback_data="admin:back")
        builder.adjust(1)

        await message.answer(
            f"Результаты поиска '{search_query}':\n\n" + "\n".join(user_lines),
            reply_markup=builder.as_markup()
        )
        await state.set_state(UserSearch.showing_results)
