# Работа с токенами
from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.crud.bot_token import *
from bot.views.keyboards.admin import AdminAction, AdminCallback
from core.db.session import db_helper
from libs.logging import setup_logger
from utils.token import validate_token

logger = setup_logger(__name__)
router = Router()


class TokenCheck(StatesGroup):
    checking = State()


@router.callback_query(AdminCallback.filter(F.action == AdminAction.check_tokens))
async def handle_check_tokens(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Неактивные", callback_data="admin:check_inactive")
    builder.button(text="🔄 Все", callback_data="admin:check_all")
    builder.button(text="📋 Последние 10", callback_data="admin:check_recent")
    builder.button(text="◀️ Назад", callback_data="admin:back")
    builder.adjust(1)

    await callback.message.edit_text(
        "Выберите тип проверки токенов:\n\n"
        "🔍 Неактивные - проверит только неактивные токены\n"
        "🔄 Все - проверит все токены в системе\n"
        "📋 Последние 10 - проверит 10 последних добавленных токенов",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.startswith("admin:check_"))
async def handle_check_type_selection(callback: types.CallbackQuery, state: FSMContext):
    check_type = callback.data.split(":")[1]

    # Сохраняем тип проверки в состоянии
    await state.update_data(check_type=check_type)

    async with db_helper.session_factory() as session:
        tokens = await get_tokens_to_check(session, check_type)

        if not tokens:
            await callback.message.edit_text("Токены для проверки не найдены")
            await state.clear()
            return

        await state.update_data(total_tokens=len(tokens))
        await start_token_check(callback, state)


async def start_token_check(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    check_type = data['check_type']

    messages = {
        "check_inactive": "🔍 Начинаю проверку неактивных токенов...",
        "check_all": "🔄 Начинаю проверку всех токенов...",
        "check_recent": "📋 Начинаю проверку последних 10 токенов..."
    }

    builder = InlineKeyboardBuilder()
    builder.button(text="⏹ Остановить", callback_data="admin:check_cancel")

    await callback.message.edit_text(
        f"{messages[check_type]}\nВсего токенов: {data['total_tokens']}\nПроверено: 0",
        reply_markup=builder.as_markup()
    )

    await state.set_state(TokenCheck.checking)
    await check_next_token(callback, state)


async def check_next_token(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    check_type = data['check_type']
    index = data.get('current_index', 0)

    async with db_helper.session_factory() as session:
        tokens = await get_tokens_to_check(session, check_type)

        if index >= len(tokens):
            await finish_token_check(callback, state)
            return

        token = tokens[index]
        is_valid, bot_info = await validate_token(token.token)

        if is_valid:
            await update_token_after_check(
                session,
                token.id,
                is_active=True,
                bot_id=bot_info.get("id"),
                bot_name=bot_info.get("first_name"),
                bot_username=bot_info.get("username")
            )
            active_now = data.get('active_now', 0) + 1
            status = "✅ Активен"
        else:
            status = "❌ Неактивен"
            active_now = data.get('active_now', 0)

        checked = index + 1
        await state.update_data(
            current_index=checked,
            checked=checked,
            active_now=active_now,
            last_status=f"{checked}. {token.token[:4]}...{token.token[-4:]} - {status}"
        )

        await update_progress(callback, state)
        await session.commit()

        # Рекурсивно проверяем следующий токен
        await check_next_token(callback, state)


async def update_progress(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    check_type = data['check_type']

    messages = {
        "check_inactive": "🔍 Проверка неактивных токенов...",
        "check_all": "🔄 Проверка всех токенов...",
        "check_recent": "📋 Проверка последних 10 токенов..."
    }

    progress = (
        f"\nПроверено: {data['checked']}/{data['total_tokens']}\n"
        f"Активных: {data['active_now']}\n"
        f"Последний: {data['last_status']}"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="⏹ Остановить", callback_data="admin:check_cancel")

    try:
        await callback.message.edit_text(
            f"{messages[check_type]}{progress}",
            reply_markup=builder.as_markup()
        )
    except:
        pass


async def finish_token_check(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад", callback_data="admin:back")

    await callback.message.edit_text(
        f"Проверка завершена!\n\n"
        f"Всего токенов: {data['total_tokens']}\n"
        f"Проверено: {data['checked']}\n"
        f"Активных: {data['active_now']}\n"
        f"Неактивных: {data['total_tokens'] - data['active_now']}",
        reply_markup=builder.as_markup()
    )
    await state.clear()


@router.callback_query(F.data == "admin:check_cancel", TokenCheck.checking)
async def cancel_token_check(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text(
        f"Проверка прервана!\n\n"
        f"Проверено: {data.get('checked', 0)}/{data['total_tokens']}\n"
        f"Активных: {data.get('active_now', 0)}",
        reply_markup=InlineKeyboardBuilder()
        .button(text="◀️ Назад", callback_data="admin:back")
        .as_markup()
    )
    await state.clear()
