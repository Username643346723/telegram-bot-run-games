from bot.main import main
from bot.utils.logger import setup_logger
import asyncio

logger = setup_logger(__name__)

if __name__ == "__main__":
    asyncio.run(main())
