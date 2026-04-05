"""Commission repository — monthly 5% commission tracking."""

from datetime import datetime, date
from calendar import monthrange

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.models import (
    MonthlyCommission,
    Order,
    Channel,
    User,
)


async def calculate_owner_monthly_income(
    session: AsyncSession, owner_telegram_id: int, year: int, month: int
) -> int:
    """Calculate total income for a channel owner in a given month."""
    start_date = datetime(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = datetime(year, month, last_day, 23, 59, 59)

    result = await session.execute(
        select(func.coalesce(func.sum(Order.price), 0))
        .join(Channel, Order.channel_id == Channel.id)
        .where(
            Channel.owner_telegram_id == owner_telegram_id,
            Order.status.in_(["paid", "published", "completed"]),
            Order.updated_at >= start_date,
            Order.updated_at <= end_date,
        )
    )
    return result.scalar() or 0


async def get_or_create_commission(
    session: AsyncSession, owner_telegram_id: int, year: int, month: int
) -> MonthlyCommission:
    """Get existing or create new commission record for the month."""
    result = await session.execute(
        select(MonthlyCommission).where(
            MonthlyCommission.owner_telegram_id == owner_telegram_id,
            MonthlyCommission.year == year,
            MonthlyCommission.month == month,
        )
    )
    commission = result.scalar_one_or_none()

    if not commission:
        total_income = await calculate_owner_monthly_income(
            session, owner_telegram_id, year, month
        )
        commission_amount = int(total_income * 0.05)  # 5%

        _, last_day = monthrange(year, month)
        due = date(year, month, last_day)

        commission = MonthlyCommission(
            owner_telegram_id=owner_telegram_id,
            year=year,
            month=month,
            total_income=total_income,
            commission_amount=commission_amount,
            due_date=due,
        )
        session.add(commission)
        await session.commit()
        await session.refresh(commission)

    return commission


async def update_commission_income(
    session: AsyncSession, owner_telegram_id: int, year: int, month: int
):
    """Recalculate commission amount based on current income."""
    commission = await get_or_create_commission(
        session, owner_telegram_id, year, month
    )
    total_income = await calculate_owner_monthly_income(
        session, owner_telegram_id, year, month
    )
    commission.total_income = total_income
    commission.commission_amount = int(total_income * 0.05)
    await session.commit()
    return commission


async def mark_commission_paid(
    session: AsyncSession, commission_id: int, screenshot_file_id: str
):
    """Mark commission as paid with screenshot."""
    commission = await session.get(MonthlyCommission, commission_id)
    if commission:
        commission.is_paid = True
        commission.payment_screenshot_file_id = screenshot_file_id
        commission.paid_at = datetime.utcnow()
        await session.commit()
    return commission


async def confirm_commission(session: AsyncSession, commission_id: int):
    """Admin confirms commission payment."""
    commission = await session.get(MonthlyCommission, commission_id)
    if commission:
        commission.is_paid = True
        commission.paid_at = datetime.utcnow()
        await session.commit()
    return commission


async def get_unpaid_commissions(session: AsyncSession) -> list[MonthlyCommission]:
    """Get all unpaid commissions (for admin panel)."""
    result = await session.execute(
        select(MonthlyCommission)
        .where(
            MonthlyCommission.is_paid == False,
            MonthlyCommission.commission_amount > 0,
        )
        .options(selectinload(MonthlyCommission.owner))
        .order_by(MonthlyCommission.year.desc(), MonthlyCommission.month.desc())
    )
    return list(result.scalars().all())


async def get_overdue_owners(session: AsyncSession) -> list[MonthlyCommission]:
    """Get owners with overdue commissions (past due date, not paid)."""
    today = date.today()
    result = await session.execute(
        select(MonthlyCommission)
        .where(
            MonthlyCommission.is_paid == False,
            MonthlyCommission.commission_amount > 0,
            MonthlyCommission.due_date < today,
        )
        .options(selectinload(MonthlyCommission.owner))
    )
    return list(result.scalars().all())


async def deactivate_overdue_channels(session: AsyncSession) -> int:
    """Deactivate channels of owners who haven't paid commissions. Returns count."""
    overdue = await get_overdue_owners(session)
    deactivated = 0

    for commission in overdue:
        # Get all active channels for this owner
        channels_result = await session.execute(
            select(Channel).where(
                Channel.owner_telegram_id == commission.owner_telegram_id,
                Channel.is_active == True,
            )
        )
        channels = channels_result.scalars().all()
        for ch in channels:
            ch.is_active = False
            deactivated += 1

    if deactivated > 0:
        await session.commit()

    return deactivated


async def get_all_channel_owners(session: AsyncSession) -> list[int]:
    """Get telegram_ids of all users who own at least one channel."""
    result = await session.execute(
        select(Channel.owner_telegram_id).distinct()
    )
    return [row[0] for row in result.all()]


async def get_owner_income_summary(
    session: AsyncSession, year: int, month: int
) -> list[dict]:
    """Get income summary for all owners for admin panel."""
    owners = await get_all_channel_owners(session)
    summaries = []

    for owner_tid in owners:
        income = await calculate_owner_monthly_income(session, owner_tid, year, month)
        if income > 0:
            user_result = await session.execute(
                select(User).where(User.telegram_id == owner_tid)
            )
            user = user_result.scalar_one_or_none()

            commission = await get_or_create_commission(session, owner_tid, year, month)

            summaries.append({
                "owner": user,
                "income": income,
                "commission": int(income * 0.05),
                "is_paid": commission.is_paid,
                "commission_id": commission.id,
            })

    return summaries
