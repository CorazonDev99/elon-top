"""
Search handler — search channels by name/username.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from bot.locales.i18n import get_text
from bot.keyboards.main_menu import main_menu_kb, cancel_kb
from bot.database.repositories import channel_repo
from bot.utils.formatting import format_price

router = Router()


class SearchStates(StatesGroup):
    waiting_query = State()


@router.message(F.text.in_(["🔍 Qidirish", "🔍 Поиск"]))
async def start_search(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    await state.set_state(SearchStates.waiting_query)
    await message.answer(
        get_text("search.enter_query", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML",
    )


@router.message(SearchStates.waiting_query)
async def do_search(
    message: Message, session: AsyncSession, state: FSMContext, lang: str = "uz", **kwargs
):
    query = message.text.strip()
    if len(query) < 2:
        await message.answer(get_text("search.too_short", lang), parse_mode="HTML")
        return

    channels = await channel_repo.search_channels(session, query)
    await state.clear()

    if not channels:
        await message.answer(
            get_text("search.no_results", lang),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    for ch in channels:
        stars = f"⭐{ch.avg_rating}" if ch.avg_rating > 0 else ""
        subs = f"{ch.subscribers_count // 1000}K" if ch.subscribers_count >= 1000 else str(ch.subscribers_count)
        builder.button(
            text=f"📺 {ch.channel_title} ({subs}) {stars}",
            callback_data=f"ch:{ch.id}",
        )
    builder.adjust(1)

    await message.answer(
        get_text("search.results", lang, count=len(channels), query=query),
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
