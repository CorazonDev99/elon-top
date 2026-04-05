"""
Referral handler — invite friends, view stats, get bonuses.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.locales.i18n import get_text
from bot.keyboards.main_menu import main_menu_kb
from bot.database.repositories import user_repo
from bot.utils.formatting import format_price

router = Router()


@router.message(F.text.in_(["👥 Do'stlarni taklif qilish", "👥 Пригласить друзей"]))
async def show_referral(message: Message, session: AsyncSession, lang: str = "uz", **kwargs):
    user = await user_repo.get_user(session, message.from_user.id)
    if not user:
        return

    # Get bot info for invite link
    bot_info = await message.bot.get_me()
    invite_link = f"https://t.me/{bot_info.username}?start=ref_{message.from_user.id}"

    referral_count = user.referral_count or 0
    referral_bonus = user.referral_bonus or 0

    text = get_text(
        "referral.panel", lang,
        count=referral_count,
        bonus=format_price(referral_bonus),
        link=invite_link,
    )

    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_text("referral.share_btn", lang),
        url=f"https://t.me/share/url?url={invite_link}&text=" + (
            "🎯 Oson Reklama — Telegramda reklama joylashtirish bot! Obuna bo'ling!"
            if lang == "uz" else
            "🎯 Oson Reklama — бот для размещения рекламы в Telegram! Подписывайтесь!"
        ),
    )
    builder.button(
        text=get_text("referral.copy_link", lang),
        callback_data="noop",
    )
    builder.adjust(1)

    await message.answer(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )

    # Send the link separately so user can copy it
    await message.answer(
        f"🔗 <code>{invite_link}</code>",
        parse_mode="HTML",
    )
