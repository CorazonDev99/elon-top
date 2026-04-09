"""
Suggestions handler — users can send feedback/suggestions
that get forwarded to the suggestions channel.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.locales.i18n import get_text, menu_match
from bot.keyboards.main_menu import main_menu_kb, cancel_kb

router = Router()

SUGGESTIONS_CHANNEL_ID = -1003776863127


class SuggestionStates(StatesGroup):
    waiting_text = State()


@router.message(F.text.in_(menu_match("menu.suggestions")))
async def start_suggestion(
    message: Message, state: FSMContext, lang: str = "uz", **kwargs
):
    await state.set_state(SuggestionStates.waiting_text)
    await message.answer(
        get_text("suggestions.enter_text", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML",
    )


@router.message(SuggestionStates.waiting_text)
async def receive_suggestion(
    message: Message, state: FSMContext, lang: str = "uz", **kwargs
):
    user = message.from_user
    username = f"@{user.username}" if user.username else "—"
    full_name = user.full_name or "—"

    # Build the message for the channel
    channel_text = (
        f"💡 <b>Yangi taklif!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Foydalanuvchi:</b> {full_name}\n"
        f"🆔 Username: {username}\n"
        f"🔢 ID: <code>{user.id}</code>\n\n"
        f"📝 <b>Taklif:</b>\n{message.text}\n"
    )

    try:
        await message.bot.send_message(
            chat_id=SUGGESTIONS_CHANNEL_ID,
            text=channel_text,
            parse_mode="HTML",
        )
    except Exception:
        await message.answer(
            get_text("suggestions.error", lang),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )
        await state.clear()
        return

    await state.clear()
    await message.answer(
        get_text("suggestions.sent", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )
