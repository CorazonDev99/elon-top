"""Reset database — drop all tables and re-seed."""
import asyncio
from bot.database.engine import engine, async_session
from bot.database.models import Base
from bot.data.seed import seed_regions, seed_categories, seed_ad_formats


async def reset():
    print("⚠️  Dropping ALL tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("✅ All tables dropped.")

    print("🔄 Recreating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables recreated.")

    print("🌱 Seeding data...")
    async with async_session() as session:
        await seed_regions(session)
        await seed_categories(session)
        await seed_ad_formats(session)

    print("🎉 Database reset complete!")


if __name__ == "__main__":
    asyncio.run(reset())
