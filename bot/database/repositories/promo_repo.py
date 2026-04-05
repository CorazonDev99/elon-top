"""Promo code repository."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import PromoCode


async def create_promo(
    session: AsyncSession, code: str, discount_percent: int = 0,
    discount_amount: int = 0, max_uses: int = 0, expires_at=None
) -> PromoCode:
    promo = PromoCode(
        code=code.upper(),
        discount_percent=discount_percent,
        discount_amount=discount_amount,
        max_uses=max_uses,
        expires_at=expires_at,
    )
    session.add(promo)
    await session.commit()
    await session.refresh(promo)
    return promo


async def get_promo(session: AsyncSession, code: str) -> PromoCode | None:
    result = await session.execute(
        select(PromoCode).where(PromoCode.code == code.upper())
    )
    return result.scalar_one_or_none()


async def validate_promo(session: AsyncSession, code: str) -> dict:
    """Validate promo code. Returns {"valid": bool, "promo": PromoCode|None, "error": str}."""
    promo = await get_promo(session, code)

    if not promo:
        return {"valid": False, "promo": None, "error": "not_found"}
    if not promo.is_active:
        return {"valid": False, "promo": None, "error": "inactive"}
    if promo.max_uses > 0 and promo.used_count >= promo.max_uses:
        return {"valid": False, "promo": None, "error": "used_up"}
    if promo.expires_at and datetime.utcnow() > promo.expires_at:
        return {"valid": False, "promo": None, "error": "expired"}

    return {"valid": True, "promo": promo, "error": None}


async def use_promo(session: AsyncSession, code: str):
    promo = await get_promo(session, code)
    if promo:
        promo.used_count += 1
        await session.commit()


def calc_discount(promo: PromoCode, price: int) -> int:
    """Calculate discount amount for a given price."""
    if promo.discount_amount > 0:
        return min(promo.discount_amount, price)
    if promo.discount_percent > 0:
        return int(price * promo.discount_percent / 100)
    return 0


async def get_all_promos(session: AsyncSession) -> list[PromoCode]:
    result = await session.execute(
        select(PromoCode).order_by(PromoCode.created_at.desc())
    )
    return list(result.scalars().all())


async def toggle_promo(session: AsyncSession, promo_id: int):
    promo = await session.get(PromoCode, promo_id)
    if promo:
        promo.is_active = not promo.is_active
        await session.commit()
    return promo
