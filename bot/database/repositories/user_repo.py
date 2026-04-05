"""User repository — CRUD operations for users."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User


async def get_user(session: AsyncSession, telegram_id: int) -> User | None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def update_language(session: AsyncSession, telegram_id: int, lang: str):
    user = await get_user(session, telegram_id)
    if user:
        user.language = lang
        await session.commit()


async def get_all_users(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User).where(User.is_blocked == False))
    return list(result.scalars().all())


async def count_users(session: AsyncSession) -> int:
    result = await session.execute(select(func.count(User.id)))
    return result.scalar() or 0


async def block_user(session: AsyncSession, telegram_id: int):
    user = await get_user(session, telegram_id)
    if user:
        user.is_blocked = True
        await session.commit()


async def update_card_number(session: AsyncSession, telegram_id: int, card_number: str):
    user = await get_user(session, telegram_id)
    if user:
        user.card_number = card_number
        await session.commit()


async def accept_terms(session: AsyncSession, telegram_id: int):
    user = await get_user(session, telegram_id)
    if user:
        user.terms_accepted = True
        await session.commit()
