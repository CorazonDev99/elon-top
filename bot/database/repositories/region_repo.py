"""Region & District repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.models import Region, District


async def get_all_regions(session: AsyncSession) -> list[Region]:
    result = await session.execute(
        select(Region).order_by(Region.sort_order)
    )
    return list(result.scalars().all())


async def get_region(session: AsyncSession, region_id: int) -> Region | None:
    result = await session.execute(
        select(Region).where(Region.id == region_id)
    )
    return result.scalar_one_or_none()


async def get_districts_by_region(
    session: AsyncSession, region_id: int
) -> list[District]:
    result = await session.execute(
        select(District)
        .where(District.region_id == region_id)
        .order_by(District.sort_order)
    )
    return list(result.scalars().all())


async def get_district(session: AsyncSession, district_id: int) -> District | None:
    result = await session.execute(
        select(District)
        .where(District.id == district_id)
        .options(selectinload(District.region))
    )
    return result.scalar_one_or_none()
