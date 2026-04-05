"""
Global cancel handler — catches ❌ Bekor qilish / ❌ Отмена from any FSM state.
This is registered FIRST so it has priority over all other handlers.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.locales.i18n import get_text
from bot.keyboards.main_menu import main_menu_kb

router = Router()
router.name = "cancel_router"


@router.message(F.text.in_(["❌ Bekor qilish", "❌ Отмена"]))
async def global_cancel(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    """Cancel any active FSM state and return to main menu."""
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer(
            get_text("cancelled", lang),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            get_text("menu.main", lang),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )
