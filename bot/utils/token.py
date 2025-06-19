import aiohttp

from bot.handlers.bot_token import logger


async def validate_token(token: str) -> tuple[bool, dict]:
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("ok") and data.get("result"):
                        return True, data["result"]
                else:
                    logger.warning(f"Telegram API responded with status {response.status} for token: {token}")
    except Exception as e:
        logger.warning(f"Exception during token validation: {e}")
    return False, {}
