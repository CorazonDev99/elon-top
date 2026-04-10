"""
Support handler — user sends a message that gets forwarded to admin.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.locales.i18n import get_text
from bot.keyboards.main_menu import main_menu_kb
from bot.config import settings

router = Router()


class SupportStates(StatesGroup):
    waiting_message = State()


@router.message(SupportStates.waiting_message)
async def receive_support_message(
    message: Message, state: FSMContext, lang: str = "uz", **kwargs
):
    user = message.from_user
    username = f"@{user.username}" if user.username else "—"
    full_name = user.full_name or "—"

    # Build admin notification
    admin_text = (
        f"📩 <b>Qo'llab-quvvatlash xabari!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Foydalanuvchi:</b> {full_name}\n"
        f"🆔 Username: {username}\n"
        f"🔢 ID: <code>{user.id}</code>\n\n"
        f"💬 <b>Xabar:</b>\n{message.text or '(media)'}\n"
    )

    sent = False
    for admin_id in settings.admin_ids:
        try:
            # Forward the original message to admin
            await message.forward(chat_id=admin_id)
            # Also send info card
            await message.bot.send_message(
                chat_id=admin_id,
                text=admin_text,
                parse_mode="HTML",
            )
            sent = True
        except Exception:
            continue

    await state.clear()

    if sent:
        await message.answer(
            get_text("about.support_sent", lang),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            get_text("about.support_error", lang),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )
