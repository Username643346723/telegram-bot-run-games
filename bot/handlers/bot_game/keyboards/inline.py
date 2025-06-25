from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.config import settings
from enum import Enum
from typing import Optional
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData


class UserAction(str, Enum):
    show_games = "show_games"
    random_game = "random_game"
    bot_management = "bot_management"
    my_stats = "my_stats"
    help = "help"
    share_bot = "share_bot"


class UserCallback(CallbackData, prefix="user"):
    action: UserAction
    value: Optional[int] = None


def main_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(
        text="🎲 Показать доступные игры",
        callback_data=UserCallback(action=UserAction.show_games).pack()
    )
    kb.button(
        text="🎰 Случайная игра",
        callback_data=UserCallback(action=UserAction.random_game).pack()
    )

    if is_admin:
        kb.button(
            text="⚙️ Управление ботом",
            callback_data=UserCallback(action=UserAction.bot_management).pack()
        )

    kb.button(
        text="📊 Мои достижения",
        callback_data=UserCallback(action=UserAction.my_stats).pack()
    )
    kb.button(
        text="❓ Помощь",
        callback_data=UserCallback(action=UserAction.help).pack()
    )
    kb.button(
        text="📢 Поделиться ботом",
        url="https://t.me/YourBotUsername"  # fixme Заменить
    )

    kb.adjust(1)  # Два столбца

    return kb.as_markup()


def start_keyboard(game, bot_id: int) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="▶️ Играть в Telegram",
        web_app=types.WebAppInfo(
            url=settings.game.url_template.format(game_id=game.game_id)
        )
    )
    kb.button(
        text="🕹 Другие игры",
        url=settings.game.bot_ref_template.format(ref_id=bot_id)
    )
    kb.adjust(1)
    return kb.as_markup()
