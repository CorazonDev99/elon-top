"""
/start handler — welcome message, main menu, language selection, settings, about.
"""

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.locales.i18n import get_text
from bot.keyboards.main_menu import main_menu_kb, settings_kb
from bot.keyboards.admin import language_select_kb, admin_menu_kb
from bot.database.repositories import user_repo
from bot.database.models import User
from bot.config import settings

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    await state.clear()
    await message.answer(
        get_text("welcome", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )


@router.message(F.text.in_(["📢 Reklama joylashtirish", "📢 Разместить рекламу"]))
async def browse_menu(message: Message, lang: str = "uz", **kwargs):
    # Handled by browse.py — this import triggers region selection
    from bot.handlers.browse import show_regions
    await show_regions(message, lang=lang, **kwargs)


@router.message(F.text.in_(["📋 Mening buyurtmalarim", "📋 Мои заказы"]))
async def my_orders_menu(message: Message, lang: str = "uz", **kwargs):
    from bot.handlers.my_orders import show_my_orders
    await show_my_orders(message, lang=lang, **kwargs)


@router.message(F.text.in_(["📺 Mening kanallarim", "📺 Мои каналы"]))
async def my_channels_menu(message: Message, lang: str = "uz", **kwargs):
    from bot.handlers.channel_owner import show_my_channels
    await show_my_channels(message, lang=lang, **kwargs)


@router.message(F.text.in_(["⚙️ Sozlamalar", "⚙️ Настройки"]))
async def settings_menu(message: Message, lang: str = "uz", **kwargs):
    # Check if admin
    if message.from_user.id in settings.admin_ids:
        await message.answer(
            get_text("admin.panel", lang),
            reply_markup=admin_menu_kb(lang),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            get_text("menu.main", lang),
            reply_markup=settings_kb(lang),
            parse_mode="HTML",
        )


@router.message(F.text.in_(["🌐 Tilni o'zgartirish", "🌐 Сменить язык"]))
async def change_language(message: Message, **kwargs):
    await message.answer(
        get_text("lang.select"),
        reply_markup=language_select_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("lang:"))
async def set_language(
    callback: CallbackQuery,
    session: AsyncSession,
    **kwargs,
):
    lang = callback.data.split(":")[1]
    await user_repo.update_language(session, callback.from_user.id, lang)
    await callback.message.edit_text(
        get_text("lang.changed", lang),
        parse_mode="HTML",
    )
    await callback.message.answer(
        get_text("menu.main", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(F.text.in_(["ℹ️ Bot haqida", "ℹ️ О боте"]))
async def about(message: Message, lang: str = "uz", **kwargs):
    await message.answer(
        get_text("about", lang),
        parse_mode="HTML",
    )


@router.message(F.text.in_(["🏠 Bosh menyu", "🏠 Главное меню"]))
async def home(message: Message, state: FSMContext, lang: str = "uz", **kwargs):
    await state.clear()
    await message.answer(
        get_text("menu.main", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )

