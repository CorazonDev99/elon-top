"""Middleware that auto-registers users on first interaction."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User


class UserRegisterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data.get("session")
        if not session:
            return await handler(event, data)

        # Extract user from update
        user = None
        if isinstance(event, Update):
            if event.message and event.message.from_user:
                user = event.message.from_user
            elif event.callback_query and event.callback_query.from_user:
                user = event.callback_query.from_user

        if not user or user.is_bot:
            return await handler(event, data)

        # Check if user exists
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            db_user = User(
                telegram_id=user.id,
                full_name=user.full_name,
                username=user.username,
                language="uz",
            )
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
        else:
            # Update user info if changed
            changed = False
            if db_user.full_name != user.full_name:
                db_user.full_name = user.full_name
                changed = True
            if db_user.username != user.username:
                db_user.username = user.username
                changed = True
            if changed:
                await session.commit()

        data["db_user"] = db_user
        data["lang"] = db_user.language or "uz"

        return await handler(event, data)
