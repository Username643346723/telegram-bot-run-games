from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Game


async def get_all_games(session: AsyncSession) -> Sequence[Game]:
    """Получить все игры"""
    stmt = select(Game).order_by(Game.id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_game_by_id(session: AsyncSession, game_id: int) -> Game | None:
    """Получить игру по её внешнему game_id"""
    stmt = select(Game).where(Game.game_id == game_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

# fixme подправить остальной код с учетом добавления новых функций
async def create_game(
        session: AsyncSession,
        *,
        game_id: int,
        title: str,
        image: str,
        descriptions: str,
        site_url: str,
        play_url: str,
        category: str | None = None,
        rating: float = 0.0,
        tags: list[str] | None = None
) -> Game:
    """Создать новую игру"""
    game = Game(
        game_id=game_id,
        title=title,
        image=image,
        descriptions=descriptions,
        site_url=site_url,
        play_url=play_url,
        category=category,
        rating=rating,
        tags=tags
    )
    session.add(game)
    await session.commit()
    await session.refresh(game)
    return game


async def update_game(
        session: AsyncSession,
        game_id: int,
        *,
        title: str | None = None,
        image: str | None = None,
        descriptions: str | None = None,
        site_url: str | None = None,
        play_url: str | None = None,
        category: str | None = None,
        rating: float | None = None,
        tags: list[str] | None = None
) -> Game | None:
    """Обновить игру по game_id"""
    game = await get_game_by_id(session, game_id)
    if game is None:
        return None

    if title is not None:
        game.title = title
    if image is not None:
        game.image = image
    if descriptions is not None:
        game.descriptions = descriptions
    if site_url is not None:
        game.site_url = site_url
    if play_url is not None:
        game.play_url = play_url
    if category is not None:
        game.category = category
    if rating is not None:
        game.rating = rating
    if tags is not None:
        game.tags = tags

    await session.commit()
    await session.refresh(game)
    return game


async def delete_game(session: AsyncSession, game_id: int) -> bool:
    """Удалить игру по game_id"""
    game = await get_game_by_id(session, game_id)
    if game is None:
        return False

    await session.delete(game)
    await session.commit()
    return True


async def search_games(session: AsyncSession, query: str, limit: int = 20) -> Sequence[Game]:
    """Поиск игр по описанию или названию"""
    stmt = (
        select(Game)
        .where(
            Game.descriptions.ilike(f"%{query}%") | Game.title.ilike(f"%{query}%")
        )
        .order_by(Game.id)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_games_paginated(session: AsyncSession, offset: int = 0, limit: int = 20) -> Sequence[Game]:
    """Получить игры с пагинацией"""
    stmt = (
        select(Game)
        .order_by(Game.id)
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def bulk_insert_games(session: AsyncSession, games_data: list[dict]) -> None:
    """Массовое добавление игр"""
    session.add_all([Game(**data) for data in games_data])
    await session.commit()
