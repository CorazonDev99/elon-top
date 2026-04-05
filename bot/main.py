"""
Elon Top Bot — Entry point.
Initializes the bot, dispatcher, middleware, routers, and starts polling.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from bot.config import settings
from bot.database.engine import engine
from bot.database.models import Base
from bot.data.seed import run_seed

# Middleware
from bot.middlewares.db_session import DbSessionMiddleware
from bot.middlewares.user_register import UserRegisterMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware

# Handlers (routers)
from bot.handlers.start import router as start_router
from bot.handlers.cancel import router as cancel_router
from bot.handlers.browse import router as browse_router
from bot.handlers.order import router as order_router
from bot.handlers.my_orders import router as my_orders_router
from bot.handlers.channel_owner import router as channel_owner_router
from bot.handlers.admin import router as admin_router
from bot.handlers.search import router as search_router
from bot.handlers.extras import router as extras_router
from bot.handlers.referral import router as referral_router


async def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
    logger = logging.getLogger(__name__)

    logger.info("🚀 Starting Elon Top Bot...")

    # Create tables and seed data
    logger.info("📦 Setting up database...")
    await run_seed()

    # Redis FSM storage
    redis = Redis.from_url(settings.redis_url)
    storage = RedisStorage(redis=redis)

    # Bot instance
    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Dispatcher
    dp = Dispatcher(storage=storage)

    # Register middleware (order matters: db_session first, then user_register)
    dp.update.middleware(ThrottlingMiddleware(rate_limit=0.5))
    dp.update.middleware(DbSessionMiddleware())
    dp.update.middleware(UserRegisterMiddleware())

    # Register routers (order matters!)
    dp.include_router(cancel_router)  # Global cancel — MUST be first!
    dp.include_router(search_router)  # Search
    dp.include_router(extras_router)  # Rating, report, promo, repeat
    dp.include_router(referral_router)  # Invite friends
    dp.include_router(channel_owner_router)
    dp.include_router(order_router)
    dp.include_router(admin_router)
    dp.include_router(browse_router)
    dp.include_router(my_orders_router)
    dp.include_router(start_router)  # Most generic — last

    # Start scheduler (commission reminders + auto-deactivation)
    from bot.utils.scheduler import scheduler_loop

    scheduler_task = asyncio.create_task(scheduler_loop(bot))

    # Start polling
    logger.info("✅ Bot is ready! Starting polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler_task.cancel()
        await bot.session.close()
        await engine.dispose()
        await redis.close()
        logger.info("🛑 Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
