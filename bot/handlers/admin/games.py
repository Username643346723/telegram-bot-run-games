# Управление играми
from math import ceil

from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.crud.bot_token import *
from bot.crud.games import get_all_games, delete_game, get_game_by_id, get_games_paginated, create_game
from bot.crud.user import get_recent_users, search_users
from bot.views.keyboards.admin import AdminCallback, games_main_kb, GamesCallback, GameAction, games_list_kb, game_detail_kb
from core.db.session import db_helper
from libs.logging import setup_logger

logger = setup_logger(__name__)
router = Router()
PAGE_SIZE = 5


class AddGameStates(StatesGroup):
    game_id = State()
    image = State()
    descriptions = State()


@router.callback_query(AdminCallback.filter(F.action == "games"))
async def handle_games_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("🎮 Управление играми:", reply_markup=games_main_kb())


@router.callback_query(GamesCallback.filter(F.action == GameAction.list))
async def handle_game_list(callback: types.CallbackQuery, callback_data: GamesCallback):
    page = callback_data.page or 0
    offset = page * PAGE_SIZE

    async with db_helper.session_factory() as session:
        all_games = await get_all_games(session)
        total = len(all_games)
        total_pages = ceil(total / PAGE_SIZE)

        games = await get_games_paginated(session, offset=offset, limit=PAGE_SIZE)

    if not games:
        text = "❌ На этой странице игр нет."
    else:
        lines = [f"<b>🎮 Страница {page + 1} из {total_pages}</b>\n"]
        for i, game in enumerate(games, start=offset + 1):
            lines.append(
                f"<b>{i}. {game.descriptions[:40]}...</b>\n"
                f"🆔 <code>{game.game_id}</code>\n"
                f"🖼 <a href=\"{game.image}\">Обложка</a>\n"
                f"\n"
            )
        text = "\n".join(lines)

    await callback.message.edit_text(
        text=text,
        reply_markup=games_list_kb(games=games, page=page, total_pages=total_pages),
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@router.callback_query(GamesCallback.filter(F.action == GameAction.add))
async def handle_game_add(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🆔 Введите внешний ID игры (целое число):\n\n❌ Для отмены введите /cancel")
    await state.set_state(AddGameStates.game_id)


@router.message(AddGameStates.game_id)
async def process_game_id(message: types.Message, state: FSMContext):
    try:
        game_id = int(message.text)
    except ValueError:
        await message.answer("❌ Введите корректное число!")
        return

    # Проверим, не существует ли уже такая игра
    async with db_helper.session_factory() as session:
        existing = await get_game_by_id(session, game_id)
        if existing:
            await message.answer("❌ Игра с таким ID уже существует.")
            return

    await state.update_data(game_id=game_id)
    await message.answer("🖼 Теперь отправьте ссылку на изображение:")
    await state.set_state(AddGameStates.image)


@router.message(AddGameStates.image)
async def process_game_image(message: types.Message, state: FSMContext):
    image = message.text.strip()

    if not image.startswith("http"):
        await message.answer("❌ Это должна быть ссылка (URL). Попробуйте ещё раз:")
        return

    await state.update_data(image=image)
    await message.answer("📝 Теперь отправьте описание (можно с HTML):")
    await state.set_state(AddGameStates.descriptions)


@router.message(AddGameStates.descriptions)
async def process_game_description(message: types.Message, state: FSMContext):
    descriptions = message.html_text.strip()
    data = await state.get_data()

    async with db_helper.session_factory() as session:
        game = await create_game(
            session,
            game_id=data["game_id"],
            image=data["image"],
            descriptions=descriptions
        )

    await message.answer(
        f"✅ Игра добавлена!\nID: {game.game_id}\n\nВернуться в меню: /admin",
        disable_web_page_preview=True
    )
    await state.clear()


@router.message(F.text == "/cancel")
async def cancel_fsm(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Добавление отменено.")


@router.callback_query(GamesCallback.filter(F.action == GameAction.view))
async def handle_game_view(callback: types.CallbackQuery, callback_data: GamesCallback):
    game_id = callback_data.game_id
    if not game_id:
        await callback.answer("Игра не найдена.")
        return

    async with db_helper.session_factory() as session:
        game = await get_game_by_id(session, game_id=game_id)
        if not game:
            await callback.answer("Игра не найдена.")
            return

    text = (
        f"<b>🎮 Игра: {game.descriptions[:40]}...</b>\n"
        f"🆔 <code>{game.game_id}</code>\n"
        f"🖼 <a href=\"{game.image}\">Ссылка на изображение</a>\n\n"
        f"<i>{game.descriptions[:500]}...</i>"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=game_detail_kb(game_id),
        parse_mode="HTML",
        disable_web_page_preview=False
    )


@router.callback_query(GamesCallback.filter(F.action == GameAction.delete))
async def handle_game_delete(callback: types.CallbackQuery, callback_data: GamesCallback):
    game_id = callback_data.game_id
    if game_id is None:
        await callback.answer("Ошибка: game_id не задан")
        return

    async with db_helper.session_factory() as session:
        success = await delete_game(session, game_id)

    if success:
        await callback.message.edit_text(f"✅ Игра {game_id} удалена", reply_markup=games_main_kb())
    else:
        await callback.message.edit_text(f"❌ Не удалось удалить игру {game_id}", reply_markup=games_main_kb())


@router.callback_query(GamesCallback.filter(F.action == GameAction.back))
async def handle_games_back(callback: types.CallbackQuery):
    from bot.views.keyboards.admin import admin_main_kb
    await callback.message.edit_text("Панель администратора:", reply_markup=admin_main_kb())
