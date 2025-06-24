from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from enum import Enum
from typing import Sequence


class AdminAction(str, Enum):
    users_list = "users_list"
    user_search = "user_search"
    check_tokens = "check_tokens"
    stats = "stats"
    settings = "settings"
    games = "games"
    back = "back"


class AdminCallback(CallbackData, prefix="admin"):
    action: AdminAction
    value: int | None = None


def admin_main_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Список пользователей", callback_data=AdminCallback(action=AdminAction.users_list).pack())
    kb.button(text="🔍 Поиск пользователя", callback_data=AdminCallback(action=AdminAction.user_search).pack())
    kb.button(text="🔄 Проверить токены", callback_data=AdminCallback(action=AdminAction.check_tokens).pack())
    kb.button(text="📊 Статистика", callback_data=AdminCallback(action=AdminAction.stats).pack())
    kb.button(text="🎮 Игры", callback_data=AdminCallback(action=AdminAction.games).pack())
    kb.button(text="⚙️ Настройки", callback_data=AdminCallback(action=AdminAction.settings).pack())
    kb.adjust(1)
    return kb.as_markup()


class GameAction(str, Enum):
    list = "list"
    add = "add"
    edit = "edit"
    delete = "delete"
    view = "view"
    back = "back"


class GamesCallback(CallbackData, prefix="games"):
    action: GameAction
    game_id: int | None = None
    page: int | None = 0


def games_main_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📃 Список игр", callback_data=GamesCallback(action=GameAction.list).pack())
    kb.button(text="➕ Добавить игру", callback_data=GamesCallback(action=GameAction.add).pack())
    kb.button(text="◀️ Назад", callback_data=AdminCallback(action=AdminAction.back).pack())
    kb.adjust(1)
    return kb.as_markup()


def game_detail_kb(game_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✏️ Редактировать", callback_data=GamesCallback(action=GameAction.edit, game_id=game_id).pack())
    kb.button(text="🗑 Удалить", callback_data=GamesCallback(action=GameAction.delete, game_id=game_id).pack())
    kb.button(text="◀️ Назад", callback_data=GamesCallback(action=GameAction.list).pack())
    kb.adjust(1)
    return kb.as_markup()


def games_list_kb(games: Sequence, page: int, total_pages: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for game in games:
        kb.button(
            text=f"👁 {game.descriptions[:20]}...",
            callback_data=GamesCallback(action=GameAction.view, game_id=game.game_id).pack()
        )

    # Навигация
    if page > 0:
        kb.button(
            text="⬅️ Назад",
            callback_data=GamesCallback(action=GameAction.list, page=page - 1).pack()
        )
    if page < total_pages - 1:
        kb.button(
            text="➡️ Вперёд",
            callback_data=GamesCallback(action=GameAction.list, page=page + 1).pack()
        )

    kb.button(
        text="◀️ В меню",
        callback_data=GamesCallback(action=GameAction.back).pack()
    )

    kb.adjust(1)
    return kb.as_markup()


