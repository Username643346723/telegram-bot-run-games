import asyncio
from uuid import uuid4

from bot.models import BotToken  # путь может отличаться, поправь по структуре
from core.db.session import db_helper


async def fill_missing_webhook_ids():
    async with db_helper.session_factory() as session:
        result = await session.execute(
            BotToken.__table__.select().where(BotToken.webhook_id == None)
        )
        tokens = result.fetchall()

        for row in tokens:
            token = row._mapping
            token_obj = token["BotToken"] if "BotToken" in token else token  # в зависимости от select

            token_obj.webhook_id = uuid4().hex
            session.add(token_obj)

        await session.commit()
        print(f"Обновлено {len(tokens)} записей")


asyncio.run(fill_missing_webhook_ids())
