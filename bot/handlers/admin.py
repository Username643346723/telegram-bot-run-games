from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import settings
from bot.crud.bot_token import *
from bot.crud.stats import get_system_stats
from bot.crud.user import get_recent_users, search_users
from bot.models import db_helper
from bot.utils.token import validate_token

logger = setup_logger(__name__)
router = Router()
router.message.filter(F.from_user.id.in_(settings.tg.admins_id))


class UserSearch(StatesGroup):
    waiting_for_query = State()
    showing_results = State()


class TokenCheck(StatesGroup):
    checking = State()


# Главное меню администратора
async def get_admin_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Список пользователей", callback_data="admin:users_list")
    builder.button(text="🔍 Поиск пользователя", callback_data="admin:user_search")
    builder.button(text="🔄 Проверить токены", callback_data="admin:check_tokens")
    builder.button(text="📊 Статистика", callback_data="admin:stats")
    builder.button(text="⚙️ Настройки", callback_data="admin:settings")
    builder.adjust(1)
    return builder.as_markup()


@router.message(F.text == "/admin")
async def admin_panel(message: types.Message):
    await message.answer(
        "Панель администратора:",
        reply_markup=await get_admin_menu()
    )


@router.callback_query(F.data == "admin:users_list")
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


@router.callback_query(F.data == "admin:user_search")
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


@router.callback_query(F.data == "admin:check_tokens")
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


@router.callback_query(F.data == "admin:stats")
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


@router.callback_query(F.data == "admin:settings")
async def handle_settings(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Настройки администратора:",
        reply_markup=InlineKeyboardBuilder()
        .button(text="Добавить админа", callback_data="admin:add_admin")
        .button(text="◀️ Назад", callback_data="admin:back")
        .as_markup()
    )


# Обработчик кнопки "Назад"
@router.callback_query(F.data == "admin:back")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Панель администратора:",
        reply_markup=await get_admin_menu()
    )
