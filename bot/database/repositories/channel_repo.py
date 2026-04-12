"""Channel repository — CRUD operations for channels."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.models import Channel, ChannelPricing, Category, AdFormat


async def get_categories(session: AsyncSession) -> list[Category]:
    result = await session.execute(
        select(Category).order_by(Category.sort_order)
    )
    return list(result.scalars().all())


async def get_category(session: AsyncSession, category_id: int) -> Category | None:
    result = await session.execute(
        select(Category).where(Category.id == category_id)
    )
    return result.scalar_one_or_none()


async def get_ad_formats(session: AsyncSession) -> list[AdFormat]:
    result = await session.execute(
        select(AdFormat).order_by(AdFormat.sort_order)
    )
    return list(result.scalars().all())


async def get_ad_format(session: AsyncSession, format_id: int) -> AdFormat | None:
    result = await session.execute(
        select(AdFormat).where(AdFormat.id == format_id)
    )
    return result.scalar_one_or_none()


async def get_channel_by_username(session: AsyncSession, username: str) -> Channel | None:
    """Check if a channel/group with this username already exists."""
    result = await session.execute(
        select(Channel).where(Channel.channel_username == username)
    )
    return result.scalar_one_or_none()


async def get_channels_by_district(
    session: AsyncSession, district_id: int
) -> list[Channel]:
    """Get channels in a specific district + channels available for all regions."""
    from sqlalchemy import or_

    result = await session.execute(
        select(Channel)
        .where(
            Channel.is_active == True,
            Channel.is_verified == True,
            or_(
                Channel.district_id == district_id,
                # Include channels registered for ALL regions (NULL = whole country)
                Channel.region_id.is_(None),
            ),
        )
        .options(
            selectinload(Channel.category),
            selectinload(Channel.pricing).selectinload(ChannelPricing.ad_format),
            selectinload(Channel.district),
        )
        .order_by(Channel.subscribers_count.desc())
    )
    return list(result.scalars().all())


async def get_channels_by_region(
    session: AsyncSession, region_id: int
) -> list[Channel]:
    """Get all active+verified channels in a region (all districts) + channels for all regions."""
    from bot.database.models import District
    from sqlalchemy import or_

    result = await session.execute(
        select(Channel)
        .outerjoin(District, Channel.district_id == District.id)
        .where(
            Channel.is_active == True,
            Channel.is_verified == True,
            or_(
                District.region_id == region_id,
                Channel.region_id == region_id,
                # Include channels registered for ALL regions (NULL = whole country)
                Channel.region_id.is_(None),
            ),
        )
        .options(
            selectinload(Channel.category),
            selectinload(Channel.pricing).selectinload(ChannelPricing.ad_format),
            selectinload(Channel.district),
        )
        .order_by(Channel.subscribers_count.desc())
    )
    return list(result.scalars().all())


async def get_all_active_channels(session: AsyncSession) -> list[Channel]:
    """Get all active+verified channels in the system."""
    result = await session.execute(
        select(Channel)
        .where(
            Channel.is_active == True,
            Channel.is_verified == True,
        )
        .options(
            selectinload(Channel.category),
            selectinload(Channel.pricing).selectinload(ChannelPricing.ad_format),
            selectinload(Channel.district),
        )
        .order_by(Channel.subscribers_count.desc())
    )
    return list(result.scalars().all())


async def get_channel(session: AsyncSession, channel_id: int) -> Channel | None:
    from bot.database.models import District

    result = await session.execute(
        select(Channel)
        .where(Channel.id == channel_id)
        .options(
            selectinload(Channel.category),
            selectinload(Channel.district).selectinload(District.region),
            selectinload(Channel.pricing).selectinload(ChannelPricing.ad_format),
            selectinload(Channel.owner),
        )
    )
    return result.scalar_one_or_none()


async def get_channel_full(session: AsyncSession, channel_id: int) -> Channel | None:
    """Get channel with all relations loaded."""
    from bot.database.models import District, Region

    result = await session.execute(
        select(Channel)
        .where(Channel.id == channel_id)
        .options(
            selectinload(Channel.category),
            selectinload(Channel.district).selectinload(District.region),
            selectinload(Channel.pricing).selectinload(ChannelPricing.ad_format),
            selectinload(Channel.owner),
        )
    )
    return result.scalar_one_or_none()


async def get_channels_by_owner(
    session: AsyncSession, telegram_id: int
) -> list[Channel]:
    result = await session.execute(
        select(Channel)
        .where(Channel.owner_telegram_id == telegram_id)
        .options(
            selectinload(Channel.category),
            selectinload(Channel.pricing).selectinload(ChannelPricing.ad_format),
        )
        .order_by(Channel.created_at.desc())
    )
    return list(result.scalars().all())


async def create_channel(
    session: AsyncSession,
    owner_telegram_id: int,
    channel_username: str,
    channel_title: str,
    district_id: int | None,
    category_id: int,
    subscribers_count: int,
    avg_views: int,
    description: str,
    prices: dict[int, int],  # {ad_format_id: price}
    is_group: bool = False,
    region_id: int | None = None,
) -> Channel:
    channel = Channel(
        owner_telegram_id=owner_telegram_id,
        channel_username=channel_username,
        channel_title=channel_title,
        district_id=district_id,
        region_id=region_id,
        category_id=category_id,
        subscribers_count=subscribers_count,
        avg_views=avg_views,
        description=description,
        is_verified=False,
        is_active=True,
        is_group=is_group,
    )
    session.add(channel)
    await session.flush()

    for format_id, price in prices.items():
        if price > 0:
            pricing = ChannelPricing(
                channel_id=channel.id,
                ad_format_id=format_id,
                price=price,
            )
            session.add(pricing)

    await session.commit()
    await session.refresh(channel)
    return channel


async def update_channel_prices(
    session: AsyncSession, channel_id: int, prices: dict[int, int]
):
    """Update prices for a channel — delete old, insert new."""
    # Delete existing prices
    from sqlalchemy import delete
    await session.execute(
        delete(ChannelPricing).where(ChannelPricing.channel_id == channel_id)
    )

    # Insert new prices
    for format_id, price in prices.items():
        if price > 0:
            session.add(ChannelPricing(
                channel_id=channel_id,
                ad_format_id=format_id,
                price=price,
            ))

    await session.commit()


async def verify_channel(session: AsyncSession, channel_id: int, verified: bool):
    channel = await session.get(Channel, channel_id)
    if channel:
        channel.is_verified = verified
        await session.commit()


async def toggle_channel_active(session: AsyncSession, channel_id: int) -> bool:
    channel = await session.get(Channel, channel_id)
    if channel:
        channel.is_active = not channel.is_active
        await session.commit()
        return channel.is_active
    return False


async def delete_channel(session: AsyncSession, channel_id: int):
    channel = await session.get(Channel, channel_id)
    if channel:
        await session.delete(channel)
        await session.commit()


async def get_pending_channels(session: AsyncSession) -> list[Channel]:
    result = await session.execute(
        select(Channel)
        .where(Channel.is_verified == False)
        .options(
            selectinload(Channel.owner),
            selectinload(Channel.category),
            selectinload(Channel.district),
        )
        .order_by(Channel.created_at)
    )
    return list(result.scalars().all())


async def count_channels(session: AsyncSession) -> dict:
    total = await session.execute(select(func.count(Channel.id)))
    verified = await session.execute(
        select(func.count(Channel.id)).where(Channel.is_verified == True)
    )
    pending = await session.execute(
        select(func.count(Channel.id)).where(Channel.is_verified == False)
    )
    channels_only = await session.execute(
        select(func.count(Channel.id)).where(Channel.is_group == False)
    )
    groups_only = await session.execute(
        select(func.count(Channel.id)).where(Channel.is_group == True)
    )
    return {
        "total": total.scalar() or 0,
        "verified": verified.scalar() or 0,
        "pending": pending.scalar() or 0,
        "channels": channels_only.scalar() or 0,
        "groups": groups_only.scalar() or 0,
    }


# ─── Search ───
async def search_channels(session: AsyncSession, query: str) -> list[Channel]:
    """Search channels by title or username."""
    pattern = f"%{query}%"
    result = await session.execute(
        select(Channel)
        .where(
            Channel.is_verified == True,
            Channel.is_active == True,
            (Channel.channel_title.ilike(pattern) | Channel.channel_username.ilike(pattern)),
        )
        .options(
            selectinload(Channel.district),
            selectinload(Channel.category),
            selectinload(Channel.pricing).selectinload(ChannelPricing.ad_format),
        )
        .order_by(Channel.avg_rating.desc(), Channel.subscribers_count.desc())
        .limit(20)
    )
    return list(result.scalars().all())


# ─── Recommendations (similar channels) ───
async def get_similar_channels(
    session: AsyncSession, channel_id: int, limit: int = 5
) -> list[Channel]:
    """Get channels in the same category or district."""
    channel = await session.get(Channel, channel_id)
    if not channel:
        return []

    result = await session.execute(
        select(Channel)
        .where(
            Channel.id != channel_id,
            Channel.is_verified == True,
            Channel.is_active == True,
            (Channel.category_id == channel.category_id) | (Channel.district_id == channel.district_id),
        )
        .options(
            selectinload(Channel.district),
            selectinload(Channel.category),
        )
        .order_by(Channel.avg_rating.desc(), Channel.subscribers_count.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


# ─── Auto-update subscribers via Telegram API ───
async def update_channel_stats(session: AsyncSession, channel_id: int, members: int):
    channel = await session.get(Channel, channel_id)
    if channel:
        channel.subscribers_count = members
        await session.commit()
