from random import sample

from aiogram import Router, types
from aiogram.filters.command import CommandStart

from bot.crud.games import get_all_games
from bot.crud.user import create_or_update_user
from bot.handlers.bot_game.keyboards.inline import start_keyboard, main_keyboard
from core.config import settings
from core.db.session import db_helper
from libs.logging import setup_logger

logger = setup_logger(__name__)
router = Router()


async def register_user(message: types.Message):
    async with db_helper.session_factory() as session:
        await create_or_update_user(
            session,
            user_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
            language_code=message.from_user.language_code,
        )


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    logger.info(
        "User %s (%s) started bot id: %s. Username: @%s, language: %s",
        message.from_user.id,
        message.from_user.full_name,
        message.bot.id,
        message.from_user.username or "no_username",
        message.from_user.language_code or "unknown"
    )

    await register_user(message)

    # Получаем список игр и формируем приветственный текст

    # Проверка, является ли пользователь админом (пример)
    is_admin = message.from_user.id in settings.admin_ids  # допустим у тебя есть список админов

    keyboard = main_keyboard(is_admin=is_admin)

    await message.answer(
        "🎮 Добро пожаловать в мир Telegram игр!\n\n"
        "У нас есть классные игры с разным рейтингом:\n\n"
        "...список игр...\n\n"
        "Готов начать? Выбирай, что хочешь сделать дальше!",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.message(CommandStart())
async def cmd_start(message: types.Message):


    async with db_helper.session_factory() as session:
        all_games = await get_all_games(session)

    # Выбираем 3 случайные игры (или меньше, если мало)
    selected_games = sample(all_games, k=min(3, len(all_games)))

    # Формируем красивое приветствие
    welcome_text = (
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n"
        "Я помогу тебе найти классные Telegram игры.\n\n"
        "Вот несколько популярных игр прямо сейчас:"
    )

    # Отправляем каждую игру с кнопкой
    for game in selected_games:
        kb = start_keyboard(game, bot_id=message.bot.id)
        await message.answer_photo(
            photo=game.image,
            caption=game.descriptions,
            reply_markup=kb,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    await message.answer(
        "🔎 Хочешь посмотреть другие игры? Жми кнопку ниже.",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="🕹 Другие игры",
                        url=settings.game.bot_ref_template.format(ref_id=message.bot.id)
                    )
                ]
            ]
        )
    )
