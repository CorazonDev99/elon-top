"""Order repository — CRUD for orders."""

from datetime import datetime, timedelta, date

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.models import Order, Channel, ChannelPricing


async def create_order(
    session: AsyncSession,
    advertiser_telegram_id: int,
    channel_id: int,
    ad_format_id: int,
    price: int,
    ad_text: str | None = None,
    ad_media_file_id: str | None = None,
    ad_media_type: str | None = None,
    desired_date: date | None = None,
) -> Order:
    order = Order(
        advertiser_telegram_id=advertiser_telegram_id,
        channel_id=channel_id,
        ad_format_id=ad_format_id,
        price=price,
        ad_text=ad_text,
        ad_media_file_id=ad_media_file_id,
        ad_media_type=ad_media_type,
        desired_date=desired_date,
        status="pending",
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def get_order(session: AsyncSession, order_id: int) -> Order | None:
    result = await session.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.channel).selectinload(Channel.owner),
            selectinload(Order.ad_format),
            selectinload(Order.advertiser),
        )
    )
    return result.scalar_one_or_none()


async def get_orders_by_advertiser(
    session: AsyncSession, telegram_id: int
) -> list[Order]:
    result = await session.execute(
        select(Order)
        .where(Order.advertiser_telegram_id == telegram_id)
        .options(
            selectinload(Order.channel),
            selectinload(Order.ad_format),
        )
        .order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())


async def get_orders_by_channel(
    session: AsyncSession, channel_id: int, status: str | None = None
) -> list[Order]:
    query = (
        select(Order)
        .where(Order.channel_id == channel_id)
        .options(
            selectinload(Order.ad_format),
            selectinload(Order.advertiser),
        )
        .order_by(Order.created_at.desc())
    )
    if status:
        query = query.where(Order.status == status)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_pending_orders_for_owner(
    session: AsyncSession, owner_telegram_id: int
) -> list[Order]:
    """Get all pending orders for channels owned by the given user."""
    result = await session.execute(
        select(Order)
        .join(Channel)
        .where(
            Channel.owner_telegram_id == owner_telegram_id,
            Order.status == "pending",
        )
        .options(
            selectinload(Order.channel),
            selectinload(Order.ad_format),
            selectinload(Order.advertiser),
        )
        .order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())


async def update_order_status(
    session: AsyncSession,
    order_id: int,
    status: str,
    rejection_reason: str | None = None,
) -> Order | None:
    order = await session.get(Order, order_id)
    if order:
        order.status = status
        if rejection_reason:
            order.rejection_reason = rejection_reason
        order.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(order)
    return order


async def save_payment_screenshot(
    session: AsyncSession, order_id: int, file_id: str
):
    order = await session.get(Order, order_id)
    if order:
        order.payment_screenshot_file_id = file_id
        order.status = "payment_pending"
        order.updated_at = datetime.utcnow()
        await session.commit()


async def count_orders(session: AsyncSession) -> dict:
    total = await session.execute(select(func.count(Order.id)))

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = await session.execute(
        select(func.count(Order.id)).where(Order.created_at >= today)
    )

    week_ago = today - timedelta(days=7)
    week_count = await session.execute(
        select(func.count(Order.id)).where(Order.created_at >= week_ago)
    )

    return {
        "total": total.scalar() or 0,
        "today": today_count.scalar() or 0,
        "week": week_count.scalar() or 0,
    }


async def get_channel_pricing(
    session: AsyncSession, channel_id: int, ad_format_id: int
) -> ChannelPricing | None:
    result = await session.execute(
        select(ChannelPricing).where(
            ChannelPricing.channel_id == channel_id,
            ChannelPricing.ad_format_id == ad_format_id,
        )
    )
    return result.scalar_one_or_none()
