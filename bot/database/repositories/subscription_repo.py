"""Subscription repository — CRUD for weekly auto-ad subscriptions."""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from bot.database.models import Subscription


async def create_subscription(
    session: AsyncSession,
    advertiser_tid: int,
    channel_id: int,
    ad_format_id: int,
    price: int,
    frequency: str = "weekly",
    ad_text: str = None,
    ad_media_file_id: str = None,
    ad_media_type: str = None,
) -> Subscription:
    if frequency == "weekly":
        next_date = date.today() + timedelta(weeks=1)
    elif frequency == "biweekly":
        next_date = date.today() + timedelta(weeks=2)
    else:
        next_date = date.today() + timedelta(days=30)

    sub = Subscription(
        advertiser_telegram_id=advertiser_tid,
        channel_id=channel_id,
        ad_format_id=ad_format_id,
        price_per_post=price,
        frequency=frequency,
        ad_text=ad_text,
        ad_media_file_id=ad_media_file_id,
        ad_media_type=ad_media_type,
        next_post_date=next_date,
    )
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub


async def get_user_subscriptions(session: AsyncSession, advertiser_tid: int) -> list[Subscription]:
    result = await session.execute(
        select(Subscription)
        .options(joinedload(Subscription.channel), joinedload(Subscription.ad_format))
        .where(Subscription.advertiser_telegram_id == advertiser_tid)
        .order_by(Subscription.created_at.desc())
    )
    return list(result.scalars().all())


async def get_due_subscriptions(session: AsyncSession) -> list[Subscription]:
    """Get subscriptions that need to post today."""
    result = await session.execute(
        select(Subscription)
        .options(
            joinedload(Subscription.channel),
            joinedload(Subscription.ad_format),
            joinedload(Subscription.advertiser),
        )
        .where(
            Subscription.is_active == True,
            Subscription.next_post_date <= date.today(),
        )
    )
    return list(result.scalars().all())


async def advance_subscription(session: AsyncSession, sub_id: int):
    """After auto-posting, advance the next_post_date."""
    result = await session.execute(
        select(Subscription).where(Subscription.id == sub_id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return

    sub.total_posts += 1
    if sub.frequency == "weekly":
        sub.next_post_date = date.today() + timedelta(weeks=1)
    elif sub.frequency == "biweekly":
        sub.next_post_date = date.today() + timedelta(weeks=2)
    else:
        sub.next_post_date = date.today() + timedelta(days=30)

    await session.commit()


async def cancel_subscription(session: AsyncSession, sub_id: int):
    result = await session.execute(
        select(Subscription).where(Subscription.id == sub_id)
    )
    sub = result.scalar_one_or_none()
    if sub:
        sub.is_active = False
        await session.commit()
