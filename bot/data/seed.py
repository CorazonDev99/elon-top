"""
Seed script — fills the database with initial data
(regions, districts, categories, ad formats).
Run once on first setup.
"""

import asyncio

from sqlalchemy import select

from bot.database.engine import engine, async_session
from bot.database.models import Base, Region, District, Category, AdFormat
from bot.data.regions import REGIONS_DATA, CATEGORIES_DATA, AD_FORMATS_DATA


async def seed_regions(session):
    """Seed all regions and districts."""
    result = await session.execute(select(Region).limit(1))
    if result.scalar():
        print("⏭  Regions already seeded, skipping.")
        return

    for i, region_data in enumerate(REGIONS_DATA):
        region = Region(
            name_uz=region_data["name_uz"],
            name_ru=region_data["name_ru"],
            emoji=region_data["emoji"],
            sort_order=i + 1,
        )
        session.add(region)
        await session.flush()  # get region.id

        for j, dist_data in enumerate(region_data["districts"]):
            district = District(
                region_id=region.id,
                name_uz=dist_data["name_uz"],
                name_ru=dist_data["name_ru"],
                sort_order=j + 1,
            )
            session.add(district)

    await session.commit()
    print(f"✅ Seeded {len(REGIONS_DATA)} regions with districts.")


async def seed_categories(session):
    """Seed channel categories."""
    result = await session.execute(select(Category).limit(1))
    if result.scalar():
        print("⏭  Categories already seeded, skipping.")
        return

    for i, cat_data in enumerate(CATEGORIES_DATA):
        category = Category(
            name_uz=cat_data["name_uz"],
            name_ru=cat_data["name_ru"],
            emoji=cat_data["emoji"],
            sort_order=i + 1,
        )
        session.add(category)

    await session.commit()
    print(f"✅ Seeded {len(CATEGORIES_DATA)} categories.")


async def seed_ad_formats(session):
    """Seed ad formats."""
    result = await session.execute(select(AdFormat).limit(1))
    if result.scalar():
        print("⏭  Ad formats already seeded, skipping.")
        return

    for i, fmt_data in enumerate(AD_FORMATS_DATA):
        ad_format = AdFormat(
            name_uz=fmt_data["name_uz"],
            name_ru=fmt_data["name_ru"],
            description_uz=fmt_data.get("description_uz"),
            description_ru=fmt_data.get("description_ru"),
            sort_order=i + 1,
        )
        session.add(ad_format)

    await session.commit()
    print(f"✅ Seeded {len(AD_FORMATS_DATA)} ad formats.")


async def create_tables():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created.")


async def run_seed():
    """Main seed function."""
    print("🌱 Starting database seed...")
    await create_tables()

    async with async_session() as session:
        await seed_regions(session)
        await seed_categories(session)
        await seed_ad_formats(session)

    print("🎉 Seed completed!")


if __name__ == "__main__":
    asyncio.run(run_seed())
