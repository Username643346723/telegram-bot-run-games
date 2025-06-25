from aiogram import Router
from aiogram import types
from aiogram.filters.command import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from random import choice
from bot.crud.user import create_or_update_user
from bot.crud.games import get_all_games
from core.db.session import db_helper
from libs.logging import setup_logger
from core.config import settings


logger = setup_logger(__name__)
router = Router()


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

    async with db_helper.session_factory() as session:
        await create_or_update_user(
            session,
            user_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
            language_code=message.from_user.language_code,
        )

    async with db_helper.session_factory() as session:
        game = await get_all_games(session)

    random_game = choice(game)
    kb = InlineKeyboardBuilder()
    kb.button(
        text='▶️ Играть в Telegram',
        web_app=types.WebAppInfo(url=settings.game.url_template.format(game_id=random_game.game_id))
    )
    kb.button(
        text='🕹 Другие игры',
        url=settings.game.bot_ref_template.format(ref_id=message.bot.id)
    )
    kb.adjust(1)

    await message.answer_photo(
        photo=random_game.image,
        caption=random_game.descriptions,
        disable_web_page_preview=True,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
